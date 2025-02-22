
# Al-Powered-Schema-Selection-for-NL-to-SQL-Pipelines
<p>
  Problem Statement:<br>
  
Task is to build an Al-driven system that dynamically selects the most relevant tables from a database schema based on a user's natural language query. This system should:<br>
1. Analyze the NL query to understand the required data.<br>
2. Scan the available table schema (provided in JSON or YAML format) and filter out irrelevant tables.<br>
3. Return the most relevant subset of tables and their schema in JSON or YAML format, optimizing the information sent to the NL to SQL model.</p>

<p>
  Solutions which the code is able to solve:<br>
  
1.NL Query Analysis: Uses SentenceTransformer to encode user queries, understanding context and intent.<br>
2.Relevant Table Selection: select_relevant_tables() filters schema using cosine similarity, reducing schema size for NL-to-SQL conversion.<br>
3.Optimized NL-to-SQL Conversion: query_gemini() sends only relevant tables to the Gemini model, improving efficiency and reducing token usage.<br>
4.Efficient Database Management: /create_database creates tables from JSON, inserting data only if tables are empty.<br>
5.Query Execution & Results: /query converts NL queries into SQL, executes them, and returns results in JSON format.<br>
6.Robust Error Handling: Checks for API keys, schema availability, invalid files, and query errors.<br>
7.Efficient API Design: Provides endpoints for database creation, querying, and result download.<br>
</p>
