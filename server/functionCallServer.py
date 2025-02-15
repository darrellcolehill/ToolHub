import os
from dotenv import load_dotenv
import requests
import json
import chromadb
from sentence_transformers import SentenceTransformer
from flask import Flask, jsonify, request
import re
from tqdm import tqdm
import subprocess
import sys

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

def perform_tool_call(script_name, *args):
    """
    Runs a Python script as a separate process with given arguments.
    
    :param script_name: The name of the script to run.
    :param args: Arguments to pass to the script.
    """
    try:
        toolImplememtationRoot = "../toolImplementations"
        process = subprocess.Popen([
            sys.executable, f"{toolImplememtationRoot}/{script_name}", *args
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr = process.communicate()
        
        print("Output:")
        print(stdout)
        
        if stderr:
            print("Errors:", file=sys.stderr)
            print(stderr, file=sys.stderr)
        
    except Exception as e:
        print(f"Error running script: {e}", file=sys.stderr)


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
        
        perform_tool_call(f"{toolDefinition['name']}.py", llm_response)
        # TODO: add error handling

        return jsonify({"response": llm_response, "raw_response": response.text})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/tools', methods=['GET'])
def show_tools():
    return get_existing_tools()


@app.route('/api/refresh', methods=['POST'])
def updateVectorDB():
    # Directory containing JSON files
    toolDefinitionsPath = "../toolsDefinitions"

    # Function to check if a file already exists in ChromaDB
    def file_exists_in_db(filename):
        results = collection.get(ids=[filename])
        return len(results["ids"]) > 0  # If ID exists, return True

    updatedFiles = []
    createdFiles = []
    # Process and add/update JSON files in the vector database
    for filename in tqdm(os.listdir(toolDefinitionsPath)):
        if filename.endswith(".json"):
            file_path = os.path.join(toolDefinitionsPath, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)  # Load JSON content

            # Convert JSON into a searchable text format
            text_data = json.dumps(data, indent=2)  # Convert to string
            embedding = embedding_model.encode(text_data, convert_to_numpy=True).tolist()  # Generate embedding

            if file_exists_in_db(filename):
                # Update existing entry
                collection.update(
                    ids=[filename],  # Keep the same ID
                    embeddings=[embedding],
                    metadatas=[{"filename": filename, "path": file_path}],
                    documents=[text_data]
                )
                print(f"🔄 Updated existing file in ChromaDB: {filename}")
                updatedFiles.append(filename)
            else:
                # Add new entry
                collection.add(
                    ids=[filename],
                    embeddings=[embedding],
                    metadatas=[{"filename": filename, "path": file_path}],
                    documents=[text_data]
                )
                print(f"✅ Added new file to ChromaDB: {filename}")
                createdFiles.append(filename)

    print("🎉 All JSON files have been processed!")
    return jsonify({"created":createdFiles, "updated": updatedFiles})


if __name__ == '__main__':
    app.run(debug=True)
