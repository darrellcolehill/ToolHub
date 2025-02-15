import os
from dotenv import load_dotenv
import requests
import json
import chromadb
from sentence_transformers import SentenceTransformer
from flask import Flask, jsonify, request
import re

load_dotenv()

# ===== LLM initialization =====
api_key = os.getenv("OPENAI_API_KEY")
# Define the endpoint and model
url = "http://localhost:1234/v1/completions"
model = "hugging-quants/Llama-3.2-1B-Instruct-Q8_0-GGUF"

# Initialize ChromaDB (Persistent)
chroma_client = chromadb.PersistentClient(path="../database/chroma")
collection = chroma_client.get_or_create_collection(name="tool_json_documents")

# Load local embedding models
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")



# ===== Utility Functions =====

def parse_tool_call(toolCall, toolCallDefinition):
    # return function name and list of patameters with their values
    functionName = toolCallDefinition['name']

    parameterNames = []
    for parameter in toolCallDefinition['parameters']['properties'].keys():
        parameterNames.append(parameter)

    cleanToolCall = toolCall.replace('"', '').replace("'", '')

    patameterValues = re.findall(r'\w+=([\w\s]+)', cleanToolCall)

    toolCall = {
        'function name': functionName,
        'parameter names': parameterNames,
        'parameter values': patameterValues
    }
    return toolCall


# TODO
def perform_tool_call(toolCall):

    return ""


def get_existing_tools():
    # Returns a list of tools based on file names (without extensions)
    rootdir = '../toolsDefinitions'
    allTools = {"tools": []}

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filename_without_ext = os.path.splitext(file)[0]  # Extract filename without extension
            allTools["tools"].append(filename_without_ext)

    return allTools



# ===== server =====

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api/query', methods=['GET'])
def queryLLM():
    userQuery = request.args.get("userquery")

    if userQuery == None:
        return jsonify({"error": "Missing Prompt query parameter"}), 500
        
    query = userQuery
    query_embedding = embedding_model.encode(query, convert_to_numpy=True).tolist()

    vector_db_results = collection.query(query_embeddings=[query_embedding], n_results=2)

    json_tool_definitions = {'tools': []}
    if vector_db_results["documents"] and vector_db_results["metadatas"]:  # Ensure results are not empty
        for doc, meta in zip(vector_db_results["documents"][0], vector_db_results["metadatas"][0]):
            cur_json_tool_definition = json.loads(doc)  # Convert string to JSON
            json_tool_definitions['tools'].append(cur_json_tool_definition.get('tool', {}))  # Extract the relevant 'tool' part

    formatted_json = json.dumps(json_tool_definitions, indent=4)

    # Construct the updated query
    updated_query = f"""
    <|begin_of_text|>

    <|start_header_id|>system<|end_header_id|>
    You are an expert in composing function calls. You are given a question and a set of possible functions. 
    Your task is to determine which function(s) should be invoked to fulfill the request.  

    - If none of the functions are applicable, state that explicitly.  
    - If required parameters are missing, point that out.  
    - You MUST return function calls **ONLY** in the following format:  
    **[func_name1(param1=value1, param2=value2...), func_name2(param=value)]**  
    - DO NOT return JSON, explanations, or any other text.  

    Here is a list of available functions in JSON format for reference:  
    {formatted_json}

    Your response MUST contain **only** the function call(s) in the exact format specified.  
    **DO NOT** include JSON, extra text, or explanations.  

    <|eot_id|><|start_header_id|>end_header_id|>

    <|start_header_id|>user<|end_header_id|>
    Question: {query}

    <|start_header_id|>assistant<|end_header_id|>
    """

    data = {"model": model, "prompt": updated_query, "max_tokens": 512}

    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()  # Ensure response is valid

        # Log full response for debugging
        # print("🔍 Full API Response:", response.text)

        # Check if response is actually JSON
        try:
            result = response.json()
        except json.JSONDecodeError:
            print("⚠️ ERROR: API returned non-JSON response")
            return jsonify({"error": "LLM response is not in JSON format", "raw_response": response.text}), 500

        # Ensure expected fields exist
        if "choices" not in result or not result["choices"]:
            print("⚠️ WARNING: No 'choices' returned in response")
            return jsonify({"error": "Empty response from LLM", "raw_response": response.text}), 500

        # Extract text safely
        llm_response = result["choices"][0].get("text", "").strip()

        if not llm_response:
            print("⚠️ WARNING: LLM returned an empty string")

        toolDefinition = {}
        foundValidTool = False
        for tool in json_tool_definitions['tools']:
            if tool['name'] in llm_response:
                toolDefinition = tool
                foundValidTool = True
                break

        if foundValidTool == False:
            print("⚠️ ERROR: Could not map to valid function call")
            return jsonify({"error": "Could not map to valid function call", "raw_response": response.text}), 500
        
        parsedToolCall = parse_tool_call(llm_response, toolDefinition)
        print(f"parsed tool call: {parsedToolCall}")
        # TODO: perform function call here. 

        return jsonify({"response": llm_response, "raw_response": response.text})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/tools', methods=['GET'])
def show_tools():
    return get_existing_tools()



if __name__ == '__main__':
    app.run(debug=True)
