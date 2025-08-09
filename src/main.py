import os
import uuid
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent import init_agent, query_agent 
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_dir = os.path.dirname(os.path.abspath(__file__))
graph_folder = os.path.join(app_dir, 'graph')
os.makedirs(graph_folder, exist_ok=True)
static_dir = os.path.join(app_dir, 'static')

app.mount("/graph", StaticFiles(directory=graph_folder), name="graph")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class Query(BaseModel):
    user_input: str

@app.post("/api/ask")
async def ask(query: Query):

    _uuid = str(uuid.uuid4().hex[:8])
    graph_full_path = os.path.join(graph_folder, f"/graph_{_uuid}.png")
    full_prompt = f"""
    DEVELOPER PROMPT:
    If a graph is generated, save the graph as {graph_full_path}. Display the image with `<img src={graph_full_path} max-width=100% height=auto>`.  If multiple graphs are generated, add suffixes to the filenames and update the img src attribute accordingly.

    USER MESSAGE:
    {query.user_input}
    """

    response = query_agent(full_prompt)

    graph_url = None
    
    if os.path.exists(graph_full_path):
        graph_url = f"graph/{os.path.basename(graph_full_path)}"

    print(f"\n\nGRAPH URL : {graph_url}\n\n")
    return {
        "response": response,
        "graph_url": graph_url
    }


# Serve landing page
@app.get("/")
async def serve_frontend():
    await init_agent()
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=60 
    )
