# RAG System for Elara App 

## Overview
This project is a **Retrieval-Augmented Generation (RAG) system** designed for Egyptian high school students. It processes official educational textbooks and enables precise information retrieval to answer student queries based strictly on the curriculum.

---

## Supported Subjects
The system's knowledge base includes the following subjects:

- Arabic  
- Biology  
- Chemistry  
- Dynamics  
- English  
- Physics  
- Statics  

---

## Data Pipeline and Workflow

The project follows a structured pipeline to transform raw PDF textbooks into a searchable vector database:

### 1. Text Extraction
Text is extracted directly from official high school PDF textbooks.

### 2. Data Processing
The extracted text is processed line by line.  
Each line is treated as an individual unit for embedding to maintain simplicity and direct mapping to the source content.

### 3. Embedding
Each text line is converted into a vector embedding using the **multilingual-e5-small** model, enabling effective semantic search for both Arabic and English.

### 4. Storage (Supabase)
The system uses **Supabase** as a vector database.  
For each entry, the following are stored:

- Original text  
- Metadata (e.g., subject or source)  
- Vector embedding  

Supabase enables efficient storage and similarity search over vector data.

---

## Query Processing (How the System Answers Questions)

When a user submits a query:

1. The input question is converted into an embedding using the same **multilingual-e5-small** model.  
2. The system performs a similarity search in Supabase to retrieve the closest matching text entries.  
3. The retrieved text (context) is combined with the original query.  
4. Both the query and the retrieved context are sent to the LLM.  
5. The LLM generates a final answer based on the provided context.

---

## Technologies Used

- **Data Format:** JSONL  
- **Embedding Model:** multilingual-e5-small  
- **Database:** Supabase (Vector Storage & Similarity Search)  
