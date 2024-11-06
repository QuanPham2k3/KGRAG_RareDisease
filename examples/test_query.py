import asyncio
import json
from lightrag_c.base import QueryParam
from lightrag_c.lightrag import LightRAG
import os

from lightrag_c.llm import gemini_complete,gpt_4o_mini_complete, gemini_embedding, ollama_embedding, ollama_model_complete, openai_embedding
from lightrag_c.utils import EmbeddingFunc
WORKING_DIR = "./rare_kg2"

# Khởi tạo LightRAG với working_dir đã tạo
rag = LightRAG(
    working_dir=WORKING_DIR,
    # llm_model_func=ollama_model_complete,
    # llm_model_name="qwen2",
    # llm_model_max_async=4,
    # llm_model_max_token_size=32768,
    # llm_model_kwargs={"host": "http://localhost:11434", "options": {"num_ctx": 32768}},
    embedding_func=EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(
            texts, embed_model="nomic-embed-text", host="http://localhost:11434"
        ),
    ),

    llm_model_func=gpt_4o_mini_complete,
    # embedding_func=gemini_embedding
)

# query =''' Hãy thử chẩn đoán bệnh, ghi tên bệnh có khả năng nhất dựa vào thông tin sau:
# The patient is a two-year-old girl. Her parents are non-consanguineous. She resides in Tianjin, China.",  "Clinical Presentation": "The patient was admitted due to progressive enlargement of the abdomen resulting from hepatomegaly. Laboratory examinations revealed nocturnal fasting hypoglycemia, hyperlipidemia, and significantly elevated levels of transaminases. Hepatomegaly was confirmed with both abdominal ultrasound and abdominal computed tomography enhanced scan.", "Physical Examination": "Physical examination showed no obvious growth retardation. Furthermore, electromyography excluded myopathy, and cardiomyopathy was ruled out by electrocardiogram and echocardiography.", "Past Medical History": "There is no past medical history or familial medical disorders reported.","Initial Test Results": "Laboratory examinations revealed nocturnal fasting hypoglycemia, hyperlipidemia, and significantly elevated levels of transaminases. Abdominal ultrasound confirmed hepatomegaly. Electromyography excluded myopathy, cardiomyopathy was ruled out by electrocardiogram and echocardiography.

# ''' 
# query1='''How do IL2RG gene mutations affect the immune system and overall development in patients with severe combined immunodeficiency (SCID)?   

# '''   
# result = rag.query(query1, param=QueryParam(mode="hybrid"))
# print(result)
with open('data_test/query/queries.txt', 'r', encoding='utf-8') as f:
    questions = f.read().splitlines()

questions_l = []    
for line in questions:
    if line.startswith("Question:"):
        
        questions_l.append(line[len("Question: "):])

async def main():
    results = []
    #Lặp qua từng câu hỏi và thực hiện truy vấn
    for question in questions_l:
        query = f" {question}"
        result = await rag.aquery(query, param=QueryParam(mode="local"))
        results.append({"question": question, "result": result})


    output_file="data_test/query/answer2.json"
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(results , f, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    asyncio.run(main())