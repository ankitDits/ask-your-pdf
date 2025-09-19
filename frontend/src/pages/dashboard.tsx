import { useEffect, useState } from "react";
import { useRouter } from "next/router";

export default function Dashboard() {
  const [pdfs, setPdfs] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [uploadMsg, setUploadMsg] = useState("");
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user_id = localStorage.getItem("user_id");
    if (!token || !user_id) router.push("/login");
    fetchPDFs(token, user_id);
  }, []);

  async function fetchPDFs(token: string | null, user_id: string | null) {
    if (!token || !user_id) return;
    const res = await fetch(`http://localhost:8000/pdfs?user_id=${user_id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "ngrok-skip-browser-warning": "true"
      },
    });
    const data = await res.json();
    setPdfs(data);
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    setUploadMsg("");
    if (!file) return;
    const token = localStorage.getItem("token");
    const user_id = localStorage.getItem("user_id");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", user_id || "");
    const res = await fetch("http://localhost:8000/upload_pdf", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "ngrok-skip-browser-warning": "true" },
      body: formData,
    });
    const data = await res.json();
    if (res.ok) {
      setUploadMsg("Upload successful!");
      fetchPDFs(token, user_id);
    } else {
      setUploadMsg(data.detail || "Upload failed");
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  return (
    <div className="container dashboard-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 className="dashboard-title" style={{ marginBottom: 0 }}>Your PDF Library</h2>
        <button className="dashboard-btn" style={{ padding: "8px 18px", fontSize: "1rem" }} onClick={handleLogout}>Logout</button>
      </div>
      <form className="dashboard-form" onSubmit={handleUpload}>
        <label className="dashboard-label">
          <span className="dashboard-label-text">Select PDF to upload</span>
          <input type="file" accept="application/pdf" className="dashboard-file" onChange={e => setFile(e.target.files?.[0] || null)} />
        </label>
        <button type="submit" className="dashboard-btn">Upload PDF</button>
      </form>
      {uploadMsg && <p className={uploadMsg.includes("successful") ? "dashboard-success" : "dashboard-error"}>{uploadMsg}</p>}
      <h3 className="dashboard-list-title">Your PDFs</h3>
      <ul className="dashboard-list">
        {pdfs.map(pdf => (
          <li key={pdf.id} className="dashboard-list-item">
            <a className="dashboard-list-link" href={`/chat?pdf_id=${pdf.id}`}>{pdf.filename}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
