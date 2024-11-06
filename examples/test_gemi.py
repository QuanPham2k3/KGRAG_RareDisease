import os
import logging
from lightrag_c import LightRAG, QueryParam
from lightrag_c.llm import gemini_complete, gemini_embedding,openai_embedding,ollama_embedding, ollama_model_complete 
import asyncio
import time
from pathlib import Path

from lightrag_c.utils import EmbeddingFunc


WORKING_DIR = "./rare_kg2"

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=gemini_complete,
     
    embedding_func=EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(
            texts, embed_model="nomic-embed-text", host="http://localhost:11434"
        ),
    )
)

async def process_file(file_number):
    file_name = f"data_test/with_phenotypes/diseases_batch_{file_number}.txt"
    
    if not Path(file_name).exists():
        print(f"File {file_name} not found, skipping...")
        return "SKIP"
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Processing {file_name}...")
            with open(file_name, "r", encoding="utf-8") as f:
                await rag.ainsertDisease(f.read())
            print(f"Successfully processed {file_name}")
            return "SUCCESS"
            
        except Exception as e:
            error_msg = str(e)
            if "Resource has been exhausted" in error_msg:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Rate limit retry exhausted for {file_name}, skipping after {max_retries} attempts")
                    return "SKIP_RATE_LIMIT"
                
                wait_time = 60 * retry_count
                print(f"Hit rate limit on {file_name}, waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                await asyncio.sleep(wait_time)
                continue
            if "copyrighted material" in error_msg:
                print(f"Copyright issue detected in {file_name}, skipping...")
                return "SKIP_COPYRIGHT"
            else:
                print(f"Error processing {file_name}: {error_msg}")
                return "ERROR"
    
    return "ERROR"  # Shouldn't reach here, but just in case

async def process_range(start, end):
    current_file = start
    error_log = []
    
    while current_file <= end:
        result = await process_file(current_file)
        
        if result == "SUCCESS":
            print(f"Moving to next file...")
            current_file += 1
            await asyncio.sleep(2)
        elif result in ["SKIP", "SKIP_COPYRIGHT", "SKIP_RATE_LIMIT"]:
            reason = {
                "SKIP": "not found",
                "SKIP_COPYRIGHT": "copyright issue",
                "SKIP_RATE_LIMIT": "rate limit exhausted after 3 retries"
            }[result]
            print(f"Skipping file {current_file}: {reason}")
            error_log.append(f"File {current_file:02d}: Skipped due to {reason}")
            current_file += 1
        else:  # ERROR
            error_log.append(f"File {current_file:02d}: Failed with error")
            print(f"Moving to next file after error...")
            current_file += 1
            await asyncio.sleep(2)
    
    # Print summary at the end
    if error_log:
        print("\nProcessing Summary:")
        for error in error_log:
            print(error)
        
        # Save error log to file
        log_file = f"error_log_{start}_to_{end}.txt"
        with open(log_file, "w") as f:
            f.write("\n".join(error_log))
        print(f"\nError log saved to {log_file}")

# Run the async code
if __name__ == "__main__":
    asyncio.run(process_range(start=31, end=40))