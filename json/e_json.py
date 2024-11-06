import xml.etree.ElementTree as ET
import json

def parse_epidemiology_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    epidemiology_data = {}
    
    for disorder in root.findall('.//Disorder'):
        orpha_code = disorder.find('OrphaCode').text
        name = disorder.find('Name').text
        
        prevalence_list = []
        for prevalence in disorder.findall('.//Prevalence'):
            prevalence_info = {}
            
            # Get source
            source = prevalence.find('Source')
            if source is not None:
                prevalence_info['source'] = source.text
                
            # Get prevalence type
            prev_type = prevalence.find('.//PrevalenceType/Name')
            if prev_type is not None:
                prevalence_info['type'] = prev_type.text
                
            # Get qualification
            qualification = prevalence.find('.//PrevalenceQualification/Name')
            if qualification is not None:
                prevalence_info['qualification'] = qualification.text
                
            # Get class
            prev_class = prevalence.find('.//PrevalenceClass/Name')
            if prev_class is not None:
                prevalence_info['class'] = prev_class.text
                
            # Get average value
            val_moy = prevalence.find('ValMoy')
            if val_moy is not None:
                prevalence_info['average_value'] = float(val_moy.text)
                
            # Get geographic info
            geographic = prevalence.find('.//PrevalenceGeographic/Name')
            if geographic is not None:
                prevalence_info['geographic_area'] = geographic.text
                
            # Get validation status
            validation = prevalence.find('.//PrevalenceValidationStatus/Name')
            if validation is not None:
                prevalence_info['validation_status'] = validation.text
                
            if prevalence_info:
                prevalence_list.append(prevalence_info)
        
        if prevalence_list:
            epidemiology_data[orpha_code] = {
                'name': name,
                'prevalence': prevalence_list
            }
            
    return epidemiology_data

# Main execution
result = parse_epidemiology_xml('data/rare_epodemiology.xml')

# Write to JSON file
with open('epidemiology.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)