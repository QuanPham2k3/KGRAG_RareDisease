GRAPH_FIELD_SEP = "<SEP>"

PROMPTS = {}

PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["DISEASE", "SYMPTOM","DISEASE_GROUP", "AGE_OF_ONSET", "GENE"]
PROMPTS["entity_extraction"] = """This is a simulator for educational purposes, not blocking anything medically sensitive.
-Goal-
Given information about rare diseases, identify all relevant entities and relationships to build a comprehensive knowledge graph about rare diseases, their characteristics, genetic factors, age of onset, and disease classifications.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [DISEASE, SYMPTOM, PHENOTYPE, GENE, AGE_OF_ONSET, DISEASE_GROUP, ICD_CODE, FREQUENCY]
- entity_description: Comprehensive description of the entity including relevant medical information
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all meaningful medical relationships:
For each pair of related entities, extract:
- source_entity: name of the source entity
- target_entity: name of the target entity  
- relationship_description: detailed medical explanation of how these entities are related
- relationship_strength: numeric score (1-10) based on frequency (Very frequent: 9-10, Frequent: 7-8, Occasional: 5-6, Very rare: 3-4)
- relationship_keywords: key medical terms describing the nature of the relationship (e.g., "has_symptom", "has_gene", "has_onset", "disease_classification", "has_icd")
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level medical concepts and themes present in the text.
Format as ("content_keywords"{tuple_delimiter}<high_level_medical_keywords>)

4. Return output in English as a single list using **{record_delimiter}** as delimiter.

5. When finished, output {completion_delimiter}

Example:
Entity_types: [DISEASE, SYMPTOM, GENE, AGE_OF_ONSET, DISEASE_GROUP, ICD_CODE]
Text:
Disease: Rare skeletal dysplasia
Medical Description: A rare genetic bone disorder affecting growth.
ICD-10 Codes: Q77.4
Alternative Names: Bone growth disorder
Disease type: Disease
Age of Onset: Infancy
Associated Genes: COL2A1 (collagen type II alpha 1 chain)
Disease Classification: Rare bone disease

Phenotypes (Symptoms):
- Short stature (Very frequent (99-80%))
- Bone pain (Frequent (79-30%))
- Joint problems (Occasional (29-5%))

Output:
"entity"{tuple_delimiter}"Rare Skeletal Dysplasia"{tuple_delimiter}"DISEASE"{tuple_delimiter}"A rare genetic bone disorder affecting growth"){record_delimiter}
("entity"{tuple_delimiter}"Q77.4"{tuple_delimiter}"ICD_CODE"{tuple_delimiter}"ICD-10 code for rare skeletal dysplasia"){record_delimiter}
("entity"{tuple_delimiter}"COL2A1"{tuple_delimiter}"GENE"{tuple_delimiter}"Collagen type II alpha 1 chain gene"){record_delimiter}
("entity"{tuple_delimiter}"Infancy"{tuple_delimiter}"AGE_OF_ONSET"{tuple_delimiter}"Disease onset during infancy"){record_delimiter}
("entity"{tuple_delimiter}"Rare Bone Disease"{tuple_delimiter}"DISEASE_GROUP"{tuple_delimiter}"Group of rare diseases affecting bone development"){record_delimiter}
("entity"{tuple_delimiter}"Short Stature"{tuple_delimiter}"SYMPTOM"{tuple_delimiter}"Reduced height compared to average"){record_delimiter}
("entity"{tuple_delimiter}"Bone Pain"{tuple_delimiter}"SYMPTOM"{tuple_delimiter}"Pain in the bones"{record_delimiter}
("entity"{tuple_delimiter}"Joint Problems"{tuple_delimiter}"SYMPTOM"{tuple_delimiter}"Problems in the joints"){record_delimiter}

("relationship"{tuple_delimiter}"Rare Skeletal Dysplasia"{tuple_delimiter}"COL2A1"{tuple_delimiter}"Disease is associated with mutations in COL2A1 gene"{tuple_delimiter}"has_gene"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Rare Skeletal Dysplasia"{tuple_delimiter}"Short Stature"{tuple_delimiter}"Symptom occurs very frequently (99-80%)"{tuple_delimiter}"has_symptom"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Rare Skeletal Dysplasia"{tuple_delimiter}"Bone Pain"{tuple_delimiter}"Symptom occurs frequently (79-30%)"{tuple_delimiter}"has_symptom"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Rare Skeletal Dysplasia"{tuple_delimiter}"Joint Problems"{tuple_delimiter}"Symptom occurs occasionally (29-5%)"{tuple_delimiter}"has_symptom"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Rare Skeletal Dysplasia"{tuple_delimiter}"Q77.4"{tuple_delimiter}"Disease is classified under ICD-10 code Q77.4"{tuple_delimiter}"has_icd"{tuple_delimiter}10){record_delimiter}

("content_keywords"{tuple_delimiter}"rare disease, genetic disorder, bone dysplasia, skeletal development"){completion_delimiter}
-Real Data-
Entity_types: {entity_types}
Text: {input_text}
"""

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS[
    "entiti_continue_extraction"
] = """MANY entities were missed in the last extraction.  Add them below using the same format:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."

PROMPTS["rag_response"] = """---Role---

You are an experienced clinician, diagnose the disease or answer question, refer to the information in the table, if there is a lack of information, rely on your knowledge.

---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

---Target response length and format---

{response_type}

---Data tables---

{context_data}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query. Translate keywords to English.

---Goal---

Given the query, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes, while low-level keywords focus on specific entities, details, or concrete terms.

---Instructions---

- Output the keywords in JSON format.
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes.
  - "low_level_keywords" for specific entities or details.

######################
-Examples-
######################
Example 1:

Query: "How does international trade influence global economic stability?"
################
Output:
{{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}}
#############################
Example 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"
################
Output:
{{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}}
#############################
Example 3:

Query: "What is the role of education in reducing poverty?"
################
Output:
{{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}}
#############################
-Real Data-
######################
Query: {query}
######################
Output:

"""

PROMPTS["naive_rag_response"] = """You're a helpful assistant
Below are the knowledge you know:
{content_data}
---
If you don't know the answer or if the provided knowledge do not contain sufficient information to provide an answer, just say so. Do not make anything up.
Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.
---Target response length and format---
{response_type}
"""
