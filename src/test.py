import os
import requests
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://router.huggingface.co/hf-inference/models/intfloat/multilingual-e5-small/pipeline/feature-extraction"

def get_relevant_chunks(query, limit=1):
    try:
      
        headers = {
            "Authorization": f"Bearer {HF_API_KEY}"
        }
        payload = {"inputs": f"query: {query}"} 
        
        hf_response = requests.post(HF_API_URL, headers=headers, json=payload)
        
        if hf_response.status_code != 200:
            print(f"Hugging Face API Error: {hf_response.text}")
            return []
            
        query_vector = hf_response.json()

        response = supabase.rpc('match_documents', {
            'query_embedding': query_vector,
            'match_threshold': 0.85, 
            'match_count': limit
        }).execute()
        
        return response.data
        
    except Exception as e:
        print(f"ERROR: {e}")
        return []

if __name__ == "__main__":

    user_query =  input("")
    result = get_relevant_chunks(user_query)
    
    if not result:
        print("no relevent chunks are found")
    else:
        for i, doc in enumerate(result):
            print(f" text : {doc['content']}")
            print(f" similarity : {round(doc['similarity'], 4)}")
  