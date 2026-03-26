import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def upload_all_images(folder_path, bucket_name="elara-assets"):
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            local_path = os.path.join(folder_path, filename)
            supabase_path = f"lessons/{filename}" 

            with open(local_path, 'rb') as f:
                try: 
                    supabase.storage.from_(bucket_name).upload(
                        path=supabase_path,
                        file=f,
                        file_options={"content-type": "image/png"}
                    )
                    
                
                    url_res = supabase.storage.from_(bucket_name).get_public_url(supabase_path)
                    print(f"uploaded :{filename}  link: {url_res}")
                except Exception as e:
                    print(f"error : {filename}: {e}")

if __name__ == "__main__":
    upload_all_images("data/images")