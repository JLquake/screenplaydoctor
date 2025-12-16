import { useState } from "react";
export default function Home() {
  const [file, setFile] = useState();
  const [report, setReport] = useState();
  const [chat, setChat] = useState("");
  const [rewritten, setRewritten] = useState();

  async function uploadFile() {
    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: file,
    }).then(r => r.json());
    setReport(res.report);
  }

  async function rewrite() {
    const res = await fetch("http://localhost:8000/rewrite", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ script: report.text, note: chat }),
    }).then(r => r.json());
    setRewritten(res.newXml);
    const blob = new Blob([rewritten], { type: "application/xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "rewrite.fdx";
    a.click();
  }

  return (
    <div style={{ maxWidth: 800, margin: "auto", padding: 40 }}>
      <h1>AI Script Doctor</h1>
      <input type="file" accept=".fdx" onChange={e => setFile(e.target.files[0])} />
      <button onClick={uploadFile}>Analyse</button>
      {report && (
        <>
          <h2>Coverage</h2>
          <pre>{JSON.stringify(report, null, 2)}</pre>
          <textarea value={chat} onChange={e => setChat(e.target.value)} placeholder="Tell me what to change..." rows={4} style={{ width: "100%" }} />
          <button onClick={rewrite}>Apply Rewrite</button>
        </>
      )}
    </div>
  );
      }
