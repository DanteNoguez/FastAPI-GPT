from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.responses import StreamingResponse, HTMLResponse

import openai
import chromadb
import chromadb.config
from langchain.embeddings import OpenAIEmbeddings
from prompts import PROMPT, SYSTEM_MESSAGE

app = FastAPI()

origins = [
    '*',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def stream_response(message):
    openai.api_key = os.environ['OPENAI_API_KEY']
    query_embedding = embeddings.embed_query(message)
    docs = docsearch.query(query_embeddings=[query_embedding], n_results=4)["documents"][0]
    prompt = PROMPT.format(sources=docs, query=message)
    print(prompt) # "verbose"
    completion = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": f"{SYSTEM_MESSAGE}"},
            {"role": "user", "content": f"{prompt}"}
        ], stream=True, max_tokens=500, temperature=0)
    for line in completion:
        if 'content' in line['choices'][0]['delta']:
            yield line['choices'][0]['delta']['content']

@app.get("/", response_class=HTMLResponse)
def home():
    return "<html><body>My server is <span style='color:#D61341;'>Online</span></body></html>"

@app.on_event("startup")
async def start_event():
    global embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY'])
    persist_directory = '/path/to/directory'
    settings = chromadb.config.Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_directory)
    client = chromadb.Client(settings)
    global docsearch
    docsearch = client.get_collection(name='langchain')
     
@app.post("/response")
async def response(message: str):
    return StreamingResponse(stream_response(message), media_type="text/event-stream")