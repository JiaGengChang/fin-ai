import os
import uuid
from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent import init_agent, query_agent 
from fastapi.middleware.cors import CORSMiddleware
import asyncio

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

# "gate" to ensure model first receives init prompt
app.state.init_prompt_done = asyncio.Event()

class Query(BaseModel):
    user_input: str

@app.post("/api/ask")
async def ask(query: Query):
    global graph_folder
    _uuid = str(uuid.uuid4().hex[:8])
    graph_full_path = os.path.join(graph_folder, f"graph_{_uuid}.png")
    full_prompt = f"""
    DEVELOPER PROMPT:
    If a graph is generated, save the graph as {graph_full_path}. Display the image with `<img src={graph_full_path} max-width=100% height=auto>`.  If multiple graphs are generated, add suffixes to the filenames and update the img src attribute accordingly.

    USER MESSAGE:
    {query.user_input}
    """
    response = query_agent(full_prompt)
    return {"response": response}


# Serve landing page
@app.get("/")
async def serve_frontend():
    response = FileResponse("static/index.html")
    # Create task to send init prompt
    asyncio.create_task(init_agent(app))
    return response

# retrieve response to init prompt
@app.post("/api/init")
async def get_init_response():
    await app.state.init_prompt_done.wait()
    return PlainTextResponse(app.state.init_response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=60 
    )
