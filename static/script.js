// Function to display output with fade-in effect (controlled by CSS now)
function displayOutput(elementId, text) {
    const output = document.getElementById(elementId);
    output.textContent = text;
    output.style.display = "block"; // Ensure it’s visible
    setTimeout(() => output.style.display = "none", 5000); // Hide after 5s
}

document.getElementById("create-db-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("db_name", document.getElementById("db_name").value);
    formData.append("file", document.getElementById("json_file").files[0]);

    try {
        const response = await fetch("/create_database", { method: "POST", body: formData });
        const data = await response.json();
        displayOutput("schema-output", response.ok 
            ? `${data.message}\n\nSchema:\n${JSON.stringify(data.schema, null, 2)}` 
            : `Error: ${data.error}`);
    } catch (error) {
        displayOutput("schema-output", `Error: ${error.message}`);
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
            displayOutput("query-output", 
                `Filtered Schema:\n${JSON.stringify(data.filtered_schema, null, 2)}\n\n` +
                `SQL Query: ${data.sql_query}\n\nResults:\n${JSON.stringify(data.results, null, 2)}`);
            document.getElementById("download-options").style.display = "flex";
        } else {
            displayOutput("query-output", `Error: ${data.error}`);
        }
    } catch (error) {
        displayOutput("query-output", `Error: ${error.message}`);
    }
});

document.getElementById("download-json").addEventListener("click", () => {
    window.location.href = "/download_results/json";
});

document.getElementById("download-yaml").addEventListener("click", () => {
    window.location.href = "/download_results/yaml";
});