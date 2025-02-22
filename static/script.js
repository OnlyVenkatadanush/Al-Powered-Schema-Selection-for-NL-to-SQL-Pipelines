document.getElementById("create-db-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("db_name", document.getElementById("db_name").value);
    formData.append("file", document.getElementById("json_file").files[0]);

    try {
        const response = await fetch("/create_database", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById("schema-output").textContent = 
                `${data.message}\n\nSchema:\n${JSON.stringify(data.schema, null, 2)}`;
        } else {
            document.getElementById("schema-output").textContent = `Error: ${data.error}`;
        }
    } catch (error) {
        document.getElementById("schema-output").textContent = `Error: ${error.message}`;
    }
});

document.getElementById("query-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const queryData = {
        db_name: document.getElementById("query_db_name").value,
        query: document.getElementById("nl_query").value
    };

    try {
        const response = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(queryData)
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById("query-output").textContent = 
                `Filtered Schema:\n${JSON.stringify(data.filtered_schema, null, 2)}\n\n` +
                `SQL Query: ${data.sql_query}\n\nResults:\n${JSON.stringify(data.results, null, 2)}`;
            document.getElementById("download-link").style.display = "block";
        } else {
            document.getElementById("query-output").textContent = `Error: ${data.error}`;
        }
    } catch (error) {
        document.getElementById("query-output").textContent = `Error: ${error.message}`;
    }
});