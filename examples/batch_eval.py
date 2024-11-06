from asyncio.log import logger
import re
import json
import jsonlines
from openai import OpenAI

import os
from dotenv import load_dotenv

load_dotenv() 

openai_api_key = os.getenv('OPENAI_API_KEY')

def batch_eval(query_file, result1_file, output_file_path):
    client = OpenAI()

    questions_l = []
    with open(query_file, 'r', encoding='utf-8') as f:
         content = f.read().splitlines()
    answers1 = []

    for line in content:
        if line.startswith("Question:"):
            questions_l.append(line[len("Question: "):])    
        if line.startswith("Answer:"):
            answers1.append(line[len("Answer: "):])
    print("questions_l", questions_l)
    print("answers1", answers1)
    with open(result1_file, "r", encoding='utf-8') as f:
        answers2 = json.load(f)
    answers2 = [i["result"] for i in answers2]
    
    # with open(result2_file, "r") as f:
    #     answers2 = json.load(f)
    # answers2 = [i["result"] for i in answers2]
    requests = []
    for i, (query, answer1, answer2) in enumerate(zip(questions_l, answers1, answers2)):
        sys_prompt = """
        ---Role---
        You are an expert tasked with evaluating medical answers to a question based on three criteria: **Comprehensiveness**, **Relevance**, and **Accuracy**.

        """

        prompt = f"""
        You will evaluate two answers to the same question based on three criteria: **Comprehensiveness**, **Diversity**, and **Empowerment**.

        - **Comprehensiveness**: Does the answer thoroughly cover the important aspects and details of the question?
        - **Relevance**: Is the information directly related to the question and does it provide helpful and meaningful insights?
        - **Accuracy**: Is the answer factually correct and supported by scientific evidence or established medical guidelines?

        For each criterion, explain why answer good or bad. Then, select an overall winner based on these three categories. answer 1 is correct answer and answer 2 for evaluation.

        Here is the question:
        {query}

        Here are the two answers:

        **Answer 1: correct answer**
        {answer1}

        **Answer 2:**
        {answer2}

        Evaluate answers 2, using the three criteria listed above and provide detailed explanations for each criterion.
        Give a score about answer 2 compared to answer 1.
        Output your evaluation in the following JSON format:

        {{
            "Comprehensiveness": {{
                
                "Explanation": "[Provide explanation here]"
            }},
            "Relevance": {{
                
                "Explanation": "[Provide explanation here]"
            }},
            "Accuracy": {{
            
                "Explanation": "[Provide explanation here]"      
            }},
            "Score": {{
                "Answer 1": ,
            }}

        }}
        """

        request_data = {
            "custom_id": f"request-{i+1}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt},
                ],
            },
        }
        print(requests)
        requests.append(request_data)

    with jsonlines.open(output_file_path, mode="w") as writer:
        for request in requests:
            writer.write(request)

    print(f"Batch API requests written to {output_file_path}")

    batch_input_file = client.files.create(
        file=open(output_file_path, "rb"), purpose="batch"
    )
    batch_input_file_id = batch_input_file.id

    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "nightly eval job"},
    )

    print(f"Batch {batch.id} has been created.")


if __name__ == "__main__":
    query_file='data_test/query/queries.txt'
    result1_file='data_test/query/answer2.json'
    #result2_file='data_test/query/answer4.json'
    output_file_path='data_test/query/eval_requests.jsonl'
    batch_eval(query_file, result1_file, output_file_path)
