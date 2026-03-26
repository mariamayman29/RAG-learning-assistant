import os
import json
from supabase import create_client
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)
model = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

def upload_chunks(file_path, table_name="lessons"):
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            text = item.get("text")
            metadata = item.get("metadata", {})
            
            metadata["source_file"] = os.path.basename(file_path)
            embedding = model.embed_query(text)

            data = {
                "content": text,
                "metadata": metadata,
                "embedding": embedding
            }
            
            supabase.table(table_name).insert(data).execute()

    print(f"file uploaded successfully  {file_path}")

if __name__ == "__main__":
    chunks_folder = "data/chunks"
    for jsonl_file in os.listdir(chunks_folder):
        if jsonl_file.endswith(".jsonl"):
            upload_chunks(os.path.join(chunks_folder, jsonl_file))