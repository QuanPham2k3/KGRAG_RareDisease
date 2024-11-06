import asyncio
import json
import os
from datetime import datetime
from tqdm import tqdm

# Constants
INPUT_DIR = "json"
OUTPUT_DIR = "data_chunks"
DISEASES_PER_FILE = 10

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

async def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_disease_text(disease, agc_data, hpo_data):
    """Tạo text mô tả cho một bệnh"""
    # Get ICD-10 codes first
    icd10_codes = [
        ref['reference'] 
        for ref in disease['external_references'] 
        if ref['source'] == 'ICD-10'
    ]
    
    # Skip if no ICD-10 codes
    if not icd10_codes:
        return None
        
    orpha_code = disease['orpha_code']
    
    # Extract gene information
    genes = agc_data.get(orpha_code, {}).get('genes', [])
    gene_info = [f"{gene['symbol']} ({gene['name']})" for gene in genes] if genes else []
    
    # Create text with full information
    text = f"""Disease: {disease['name']}
Medical Description: {disease.get('definition', '')}
ICD-10 Codes: {', '.join(icd10_codes)}
Alternative Names: {disease.get('synonyms')}
Disease type: {disease.get('disorder_type')}
Age of Onset: {', '.join(agc_data.get(orpha_code, {}).get('age_of_onset', []))}
Associated Genes: {', '.join(gene_info)}
Disease Classification: {agc_data.get(orpha_code, {}).get('parent_disease', '')}

Phenotypes (Symptoms):
"""
    # Add symptoms
    hpo_info = next((h for h in hpo_data if h['orpha_code'] == orpha_code), None)
    if hpo_info and 'hpo_associations' in hpo_info:
        for hpo in hpo_info['hpo_associations']:
            text += f"- {hpo['hpo_term']} ({hpo.get('hpo_frequency', 'Unknown')})\n"
        
    return text

async def prepare_data():
    # Tạo thư mục output nếu chưa tồn tại
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Load data
    log_message("Loading JSON data...")
    agc_data = await load_json_data(f"{INPUT_DIR}/age_gen_cross.json")
    hpo_data = await load_json_data(f"{INPUT_DIR}/disease_hpo.json")
    icd_data = await load_json_data(f"{INPUT_DIR}/disease_ICD.json")

    # First pass: collect all unique diseases with ICD-10 codes
    unique_diseases = []
    processed_orpha_codes = set()
    
    log_message("Processing unique diseases...")
    for disease in tqdm(icd_data, desc="Collecting unique diseases"):
        try:
            orpha_code = disease['orpha_code']
            if orpha_code not in processed_orpha_codes:
                text = create_disease_text(disease, agc_data, hpo_data)
                if text:  # Has ICD-10 codes
                    unique_diseases.append(text)
                    processed_orpha_codes.add(orpha_code)
        except Exception as e:
            log_message(f"Warning: Failed to process disease {disease.get('name', 'Unknown')}: {str(e)}")
            continue

    # Now split unique diseases into batches
    total_unique = len(unique_diseases)
    num_files = (total_unique + DISEASES_PER_FILE - 1) // DISEASES_PER_FILE
    log_message(f"Found {total_unique} unique diseases with ICD-10 codes, splitting into {num_files} files...")

    # Save batches
    for file_idx in range(num_files):
        start_idx = file_idx * DISEASES_PER_FILE
        end_idx = min((file_idx + 1) * DISEASES_PER_FILE, total_unique)
        
        batch_texts = unique_diseases[start_idx:end_idx]
        
        if batch_texts:
            output_file = f"{OUTPUT_DIR}/diseases_batch_{file_idx + 1:02d}.txt"
            combined_text = "\n".join(batch_texts)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(combined_text)
                
            log_message(f"Saved {len(batch_texts)} diseases to {output_file}")

    log_message(f"Data preparation completed! Total unique diseases processed: {total_unique}")

if __name__ == "__main__":
    asyncio.run(prepare_data()) 