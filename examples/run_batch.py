import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  
client = OpenAI()

# file_response = client.files.content("data_test/query/eval_requests.jsonl")
# print(file_response.text)

def process_batch( input_file_path, output_file):
    '''
        Chức năng: Xử lý batch bằng cách upload file, gửi yêu cầu tới OpenAI API và kiểm tra trạng thái công việc batch cho đến khi hoàn tất.
    '''
    try:
        # Mở và tải file đầu vào jsonl để xử lý batch
        with open(input_file_path, "rb") as file:
            upload_file = client.files.create(
                file=file,
                purpose="batch"
            ) 

        # Tạo một batch job
        batch_job = client.batches.create(
            input_file_id=upload_file.id,
            endpoint='/v1/chat/completions',
            completion_window='24h',
        )

        # Giám sát trạng thái của batch job
        while batch_job.status not in ["completed", "failed", 'cancelled']:
            batch_job = client.batches.retrieve(batch_job.id)
            print(f'Batch job status: {batch_job.status}... try again in 20 seconds')
            time.sleep(20) 

        if batch_job.status == "completed":
            result_file_id = batch_job.output_file_id
            result = client.files.content(result_file_id) 
            
    
            result_lines = result.text.splitlines()

            Dict_batch = {}
            for line in result_lines:
                result_data = json.loads(line)
                cus_id = result_data['custom_id']
                Dict_batch[cus_id] = result_data

            final = []

            # Lặp qua dữ liệu đầu vào và ánh xạ theo custom_id với kết quả tương ứng từ batch
            for idx in range(len(Dict_batch)):
                custom_id = f"request-{idx + 1}"  
                # Lấy message content từ batch data 
                message_content = Dict_batch[custom_id]['response']['body']['choices'][0]['message']['content']
               
                try:
                    # Try to load the cleaned content as JSON
                    json_object = json.loads(message_content)
                    print("Valid JSON:", json_object)
                except json.JSONDecodeError:
                    print("Invalid JSON format!")
            
                                    

            # Ghi kết quả cuối cùng vào file "final_batch.json"
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(final, file, ensure_ascii=False, indent=4)
            print("Batch job completed successfully, results saved in final_batch.json")         

        else:
            print(f'Batch job failed with status {batch_job.status}')
            return None

    except Exception as e:
        print(f"Lỗi trong quá trình xử lý batch: {e}")
if __name__ == "__main__":
    
    batch_file = "data_test/query/eval_requests.jsonl"
    output_file = "data_test/query/eval_results.json"
    process_batch(batch_file, output_file)