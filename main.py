from fastapi import FastAPI
from models import QueryRequest, QueryResponse
from ollama_client import query_model

app = FastAPI(title='Local SLM Benchmarking API')

@app.get('/health')
def health():
    return {'status': 'running', 'models_available': ['llama3.2:3b', 'phi3.5', 'mistral']}

@app.post('/query', response_model=QueryResponse)
def query(request: QueryRequest):
    result = query_model(request.model, request.prompt, request.temperature)
    return QueryResponse(model=request.model, prompt=request.prompt, temperature=request.temperature, **result)