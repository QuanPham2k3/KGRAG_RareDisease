import asyncio
import json
import os
from datetime import datetime
from tqdm import tqdm

# Constants
INPUT_DIR = "json"
OUTPUT_DIR = "data_test"
WITH_PHENOTYPES_DIR = os.path.join(OUTPUT_DIR, "with_phenotypes")
NO_PHENOTYPES_DIR = os.path.join(OUTPUT_DIR, "no_phenotypes")
DISEASES_PER_FILE = 10

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

async def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_disease_text(disease, agc_data, hpo_data):
    """Tạo text mô tả cho một bệnh và xác định có phenotypes hay không"""
    # Get ICD-10 codes first
    icd10_codes = [
        ref['reference'] 
        for ref in disease['external_references'] 
        if ref['source'] == 'ICD-10'
    ]
    
    # Skip if no ICD-10 codes
    if not icd10_codes:
        return None, False
        
    orpha_code = disease['orpha_code']
    
    # Extract gene information
    genes = agc_data.get(orpha_code, {}).get('genes', [])
    gene_info = [f"{gene['symbol']} ({gene['name']})" for gene in genes] if genes else []
    
    # Create base text
    text = f"""Disease: {disease['name']}
Medical Description: {disease.get('definition', '')}
ICD-10 Codes: {', '.join(icd10_codes)}
Alternative Names: {disease.get('synonyms')}
Disease type: {disease.get('disorder_type')}
Age of Onset: {', '.join(agc_data.get(orpha_code, {}).get('age_of_onset', []))}
Associated Genes: {', '.join(gene_info)}
Disease Classification: {agc_data.get(orpha_code, {}).get('parent_disease', '')}"""

    # Check for phenotypes
    has_phenotypes = False
    phenotypes_text = "\nPhenotypes (Symptoms):\n"
    
    hpo_info = next((h for h in hpo_data if h['orpha_code'] == orpha_code), None)
    if hpo_info and 'hpo_associations' in hpo_info and hpo_info['hpo_associations']:
        has_phenotypes = True
        for hpo in hpo_info['hpo_associations']:
            phenotypes_text += f"- {hpo['hpo_term']} ({hpo.get('hpo_frequency', 'Unknown')})\n"
        text += phenotypes_text
        
    return text, has_phenotypes

async def prepare_data():
    # Create output directories
    for directory in [WITH_PHENOTYPES_DIR, NO_PHENOTYPES_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        
    # Load data
    log_message("Loading JSON data...")
    agc_data = await load_json_data(f"{INPUT_DIR}/age_gen_cross.json")
    hpo_data = await load_json_data(f"{INPUT_DIR}/disease_hpo.json")
    icd_data = await load_json_data(f"{INPUT_DIR}/disease_ICD.json")

    # Collect diseases
    diseases_with_phenotypes = []
    diseases_without_phenotypes = []
    processed_orpha_codes = set()
    
    log_message("Processing diseases...")
    for disease in tqdm(icd_data, desc="Processing diseases"):
        try:
            orpha_code = disease['orpha_code']
            if orpha_code not in processed_orpha_codes:
                text, has_phenotypes = create_disease_text(disease, agc_data, hpo_data)
                if text:  # Has ICD-10 codes
                    if has_phenotypes:
                        diseases_with_phenotypes.append(text)
                    else:
                        diseases_without_phenotypes.append(text)
                    processed_orpha_codes.add(orpha_code)
        except Exception as e:
            log_message(f"Warning: Failed to process disease {disease.get('name', 'Unknown')}: {str(e)}")
            continue

    # Save diseases with phenotypes
    total_with_phenotypes = len(diseases_with_phenotypes)
    num_files_with = (total_with_phenotypes + DISEASES_PER_FILE - 1) // DISEASES_PER_FILE
    log_message(f"Found {total_with_phenotypes} diseases with phenotypes, splitting into {num_files_with} files...")

    for file_idx in range(num_files_with):
        start_idx = file_idx * DISEASES_PER_FILE
        end_idx = min((file_idx + 1) * DISEASES_PER_FILE, total_with_phenotypes)
        batch_texts = diseases_with_phenotypes[start_idx:end_idx]
        
        if batch_texts:
            output_file = f"{WITH_PHENOTYPES_DIR}/diseases_batch_{file_idx + 1}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(batch_texts))
            log_message(f"Saved {len(batch_texts)} diseases with phenotypes to {output_file}")

    # Save diseases without phenotypes
    total_without_phenotypes = len(diseases_without_phenotypes)
    num_files_without = (total_without_phenotypes + DISEASES_PER_FILE - 1) // DISEASES_PER_FILE
    log_message(f"Found {total_without_phenotypes} diseases without phenotypes, splitting into {num_files_without} files...")

    for file_idx in range(num_files_without):
        start_idx = file_idx * DISEASES_PER_FILE
        end_idx = min((file_idx + 1) * DISEASES_PER_FILE, total_without_phenotypes)
        batch_texts = diseases_without_phenotypes[start_idx:end_idx]
        
        if batch_texts:
            output_file = f"{NO_PHENOTYPES_DIR}/diseases_batch_{file_idx + 1}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(batch_texts))
            log_message(f"Saved {len(batch_texts)} diseases without phenotypes to {output_file}")

    log_message(f"Data preparation completed!")
    log_message(f"Total diseases with phenotypes: {total_with_phenotypes}")
    log_message(f"Total diseases without phenotypes: {total_without_phenotypes}")

if __name__ == "__main__":
    asyncio.run(prepare_data())