import os
import uuid
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent import query_agent 
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
    filename = f"graph_{_uuid}.png"
    full_prompt = f"If a graph is generated, save the graph as '{filename}' in the folder '{graph_folder}'. If multiple graphs are generated, use 'graph_{_uuid}_1.png', 'graph_{_uuid}_2.png', etc to denote the different files. \n{query.user_input}"

    response = query_agent(full_prompt)

    graph_path = os.path.join(graph_folder, filename)
    graph_url = None
    
    if os.path.exists(graph_path):
        graph_url = f"graph/{filename}"

    print(f"\n\nGRAPH URL : {graph_url}\n\n")
    return {
        "response": response,
        "graph_url": graph_url
    }


# Serve landing page
@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=60 
    )
