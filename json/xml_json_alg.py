import xml.etree.ElementTree as ET
import json

def parse_age_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    age_data = {}
    for disorder in root.findall('.//Disorder'):
        orpha_code = disorder.find('OrphaCode').text
        age_list = []
        for age in disorder.findall('.//AverageAgeOfOnset/Name'):
            if age.text:
                age_list.append(age.text)
                
        if age_list:
            age_data[orpha_code] = age_list
    return age_data

def parse_gene_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    gene_data = {}
    for disorder in root.findall('.//Disorder'):
        orpha_code = disorder.find('OrphaCode').text
        genes = []
        for gene in disorder.findall('.//Gene'):
            gene_info = {
                'symbol': gene.find('Symbol').text,
                'name': gene.find('Name').text
            }
            genes.append(gene_info)
            
        if genes:
            gene_data[orpha_code] = genes
    return gene_data

def parse_cross_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    cross_data = {}
    for disorder in root.findall('.//Disorder'):
        orpha_code = disorder.find('OrphaCode').text
        name = disorder.find('Name').text
        
        # Get definition if available
        definition = None
        summary = disorder.find('.//TextSection/Contents')
        if summary is not None:
            definition = summary.text
            
        # Get parent disease
        parent = None
        assoc = disorder.find('.//DisorderDisorderAssociation/TargetDisorder/Name')
        if assoc is not None:
            parent = assoc.text
            
        cross_data[orpha_code] = {
            'name': name,
            'definition': definition,
            'parent': parent
        }
    return cross_data

def combine_data(age_data, gene_data, cross_data):
    combined = {}
    
    # Combine all unique orpha codes
    all_codes = set(list(age_data.keys()) + list(gene_data.keys()) + list(cross_data.keys()))
    
    for code in all_codes:
        disease_data = {
            'orpha_code': code,
            'name': cross_data.get(code, {}).get('name'),
            'definition': cross_data.get(code, {}).get('definition'),
            'parent_disease': cross_data.get(code, {}).get('parent'),
            'age_of_onset': age_data.get(code, []),
            'genes': gene_data.get(code, [])
        }
        combined[code] = disease_data
        
    return combined

# Main execution
age_data = parse_age_xml('data/_ages.xml')
gene_data = parse_gene_xml('data/gen_rare.xml')
cross_data = parse_cross_xml('data/Linearisation_of_disorder.xml')

result = combine_data(age_data, gene_data, cross_data)

# Write to JSON file
with open('age_gen_cross.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)