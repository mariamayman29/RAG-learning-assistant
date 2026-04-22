import logging
import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from supabase import create_client, Client



class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    huggingface_api_key: str
    hf_api_url: str = "https://router.huggingface.co/hf-inference/models/intfloat/multilingual-e5-small/pipeline/feature-extraction"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rag-retrieval-service")

app = FastAPI(
    title="Educational Chatbot Retrieval API",
    description="Microservice to fetch RAG context for students",
    version="1.1.0"
)

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

class Subject(str, Enum):
    biology = "biology"
    physics = "physics"
    chemistry = "chemistry"
    arabic = "arabic"
    dynamica = "dynamica"
    statica = "statica"
    english="english"

class QueryRequest(BaseModel):
    query: str = Field(..., description="The student's question", min_length=1)
    subject: Subject = Field(
        ..., 
        description="The subject to filter by. must be one of the exact specified subjects"
    )
    @field_validator('query')
    @classmethod
    def check_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("Field cannot be empty or consists only of whitespace")
        return value.strip()

class Chunk(BaseModel):
    text: str

class QueryResponse(BaseModel):
    chunks: list[Chunk] = Field(
        ..., 
        description="An array of the most relevant context chunks.if no chunks meet the similarity this will safely return an empty array []"
    )


async def fetch_huggingface_embedding(query: str) -> list[float]:
    headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
    payload = {"inputs": f"query: {query}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.hf_api_url, 
                headers=headers, 
                json=payload, 
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Hugging Face API returned an error: {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to generate text embeddings from Hugging Face"
            )
        except httpx.RequestError as e:
            logger.error(f"Network error connecting to Hugging Face: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Hugging Face is currently unreachable"
            )

@app.post("/get-relevant-chunks", response_model=QueryResponse)
async def get_relevant_chunks(request: QueryRequest):
    logger.info(f"Received query: '{request.query}' for subject: '{request.subject}'")
    
    query_vector = await fetch_huggingface_embedding(request.query)

    try:
        response = await run_in_threadpool(
            lambda: supabase.rpc('match_documents', {
                'query_embedding': query_vector,
                'match_threshold': 0.847, 
                'match_count': 1,
                'filter_subject': request.subject 
            }).execute()
        )
        
    except Exception as e:
        logger.error(f"Database error during similarity search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contextual data from the database."
        )

    if not response.data:
        logger.warning(f"No chunks met the 0.845 threshold for query: '{request.query}' in subject: '{request.subject}'")
        return QueryResponse(chunks=[])
        
    chunks = []
    for index, chunk_data in enumerate(response.data):
        similarity_score = round(chunk_data["similarity"], 4)
        chunk_text = chunk_data["content"]
        chunks.append(Chunk(text=chunk_data["content"]))
        
        logger.info(f"Chunk {index + 1} : {chunk_text} . for query '{request.query}' - Similarity: {similarity_score}")
    
    
    return QueryResponse(chunks=chunks)