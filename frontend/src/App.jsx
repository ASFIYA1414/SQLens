import { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const askDatabase = async () => {
  const response = await fetch(
    "http://127.0.0.1:8000/ask-database",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        host: "localhost",
        port: 5432,
        database_name: "sqlens_db",
        username: "postgres",
        password: "vjd123",
        question: question,
      }),
    }
  );

  const data = await response.json();

  setResponse(data);
};
  return (
    <div className="container">
      <h1>SQLens</h1>
      <p>AI-Powered Database Explorer</p>

      <h3>Ask your database</h3>

      <input
        type="text"
        placeholder="Enter your question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <br />
      <br />

      <button onClick={askDatabase}>
        Ask Database
        </button>

      <hr />

      {response && (
  <>
    <h3>Generated SQL</h3>

    <pre>{response.sql}</pre>

    <h3>Results</h3>

    <table border="1" cellPadding="10">
      <thead>
        <tr>
          {response.rows &&
            response.rows.length > 0 &&
            Object.keys(response.rows[0]).map((column) => (
              <th key={column}>{column}</th>
            ))}
        </tr>
      </thead>

      <tbody>
        {response.rows &&
          response.rows.map((row, index) => (
            <tr key={index}>
              {Object.values(row).map((value, i) => (
                <td key={i}>{value}</td>
              ))}
            </tr>
          ))}
      </tbody>
    </table>
  </>
)}
    </div>
  );
}

export default App;