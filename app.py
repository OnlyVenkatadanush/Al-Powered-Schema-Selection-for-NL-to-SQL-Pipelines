
import sqlite3
import google.generativeai as genai
import json
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
from sentence_transformers import SentenceTransformer, util

# Configure Gemini API
genai.configure(api_key="api_key")  # Replace with your actual API key
import sqlite3
import json
import os
import yaml  # Add PyYAML for YAML support
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
try:
    from sentence_transformers import SentenceTransformer, util
except ImportError as e:
    print(f"SentenceTransformers import error: {e}")
    exit(1)
try:
    import google.generativeai as genai
except ImportError as e:
    print(f"Google Generative AI import error: {e}")
    exit(1)

genai.configure(api_key="AIzaSyBZibOxOsqsstkXcJGrh1VaIyE7c5rx7Ck")  # Replace with your actual API key
generation_config = {"temperature": 0.9, "top_p": 1, "top_k": 1, "max_output_tokens": 2048}
model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def query_gemini(nl_query, table_structure):
    response = model.generate_content([f"Read the following table structure and generate the required SQL query for the given natural language prompt. Table structure: {table_structure}.(dont format the text just write as it is) Prompt: {nl_query}"])
    return response.text.strip()

def create_tables_and_insert_data(json_data, conn):
    cursor = conn.cursor()
    for table_name, rows in json_data.items():
        if not rows:
            continue
        columns = rows[0].keys()
        column_definitions = ", ".join([f"{col} TEXT" for col in columns])
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
        cursor.execute(create_table_query)
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            column_names = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in columns])
            insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            for row in rows:
                cursor.execute(insert_query, tuple(row.values()))
    conn.commit()

def select_relevant_tables(nl_query, schema):
    keywords = nl_query.lower().split()
    query_embedding = embedder.encode(" ".join(keywords))
    table_desc = [f"{table['name']} {' '.join(table['columns'])}" for table in schema["tables"]]
    table_embeddings = embedder.encode(table_desc)
    similarities = util.cos_sim(query_embedding, table_embeddings)[0]
    threshold = 0.5
    relevant_tables = [
        schema["tables"][i] for i in range(len(schema["tables"]))
        if similarities[i] > threshold
    ]
    return {"tables": relevant_tables}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create_database", methods=["POST"])
def create_database():
    if "db_name" not in request.form or "file" not in request.files:
        return jsonify({"error": "Database name and file required"}), 400
    
    db_name = request.form["db_name"]
    db_path = f"{db_name}.db"
    conn = sqlite3.connect(db_path)
    
    file = request.files["file"]
    if file.filename == "" or not file.filename.endswith(".json"):
        conn.close()
        return jsonify({"error": "Valid JSON file required"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    
    with open(file_path, "r") as f:
        json_data = json.load(f)
    
    schema = {"tables": [{"name": table_name, "columns": list(rows[0].keys())} for table_name, rows in json_data.items() if rows]}
    with open(os.path.join(app.config["UPLOAD_FOLDER"], f"{db_name}_schema.json"), "w") as f:
        json.dump(schema, f)
    
    create_tables_and_insert_data(json_data, conn)
    cursor = conn.cursor()
    schema_display = {table_name: [{"name": col[1], "type": col[2]} for col in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()] for table_name in json_data.keys()}
    conn.close()
    return jsonify({"message": f"Database '{db_name}' created", "schema": schema_display}), 200

@app.route("/query", methods=["POST"])
def query_database():
    data = request.get_json()
    if not data or "db_name" not in data or "query" not in data:
        return jsonify({"error": "Database name and query required"}), 400
    
    db_name = data["db_name"]
    nl_query = data["query"]
    db_path = f"{db_name}.db"
    
    if not os.path.exists(db_path):
        return jsonify({"error": f"Database '{db_name}' not found"}), 404
    
    schema_file = os.path.join(app.config["UPLOAD_FOLDER"], f"{db_name}_schema.json")
    if not os.path.exists(schema_file):
        return jsonify({"error": "Schema not found"}), 404
    
    with open(schema_file, "r") as f:
        schema = json.load(f)
    
    filtered_schema = select_relevant_tables(nl_query, schema)
    table_structure = json.dumps(filtered_schema, indent=4)
    sql_query = query_gemini(nl_query, table_structure)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results_list = [dict(zip(column_names, row)) for row in results]
        
        # Save both JSON and YAML formats
        with open("query_results.json", "w") as f:
            json.dump(results_list, f, indent=4)
        with open("query_results.yaml", "w") as f:
            yaml.dump(results_list, f, default_flow_style=False)
        
        conn.close()
        return jsonify({"sql_query": sql_query, "filtered_schema": filtered_schema, "results": results_list}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"error": f"Failed to execute query: {str(e)}"}), 500

@app.route("/download_results/<format>", methods=["GET"])
def download_results(format):
    if format == "json":
        file_path = "query_results.json"
        download_name = "query_results.json"
    elif format == "yaml":
        file_path = "query_results.yaml"
        download_name = "query_results.yaml"
    else:
        return jsonify({"error": "Invalid format"}), 400
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=download_name)
    return jsonify({"error": "No results available"}), 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
