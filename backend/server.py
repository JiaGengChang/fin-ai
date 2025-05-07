import os
import uuid
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import query_agent 
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend_dir = os.path.dirname(os.path.abspath(__file__))
graph_folder = os.path.join(backend_dir, 'graph')
os.makedirs(graph_folder, exist_ok=True)

app.mount("/graph", StaticFiles(directory=graph_folder), name="graph")

class Query(BaseModel):
    user_input: str

@app.post("/ask")
async def ask(query: Query):

    user_input = query.user_input
    filename = f"graph_{uuid.uuid4().hex[:8]}.png"
    full_prompt = f"{user_input}\nSave the graph as '{filename}' at {graph_folder} if applicable."

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

@app.get("/")
async def root():
    return {"message": "LangChain Financial Assistant is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=60 
    )
