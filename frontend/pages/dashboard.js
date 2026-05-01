import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { api } from "../lib/api";

export default function DashboardPage() {
  const [projects, setProjects] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newProject, setNewProject] = useState({ name: "", keywords: "" });
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await api.getProjects();
      setProjects(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const keywords = newProject.keywords.split(",").map((k) => k.trim()).filter(Boolean);
      if (keywords.length === 0) {
        setError("Enter at least one keyword");
        return;
      }
      await api.createProject({ name: newProject.name, keywords });
      setNewProject({ name: "", keywords: "" });
      setShowCreate(false);
      loadProjects();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <div style={styles.header}>
        <h1 style={styles.title}>Projects</h1>
        <button style={styles.createBtn} onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "+ New Project"}
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {showCreate && (
        <form onSubmit={handleCreate} style={styles.createForm}>
          <input
            placeholder="Project name"
            required
            value={newProject.name}
            onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
            style={styles.input}
          />
          <input
            placeholder="Keywords (comma-separated)"
            required
            value={newProject.keywords}
            onChange={(e) => setNewProject({ ...newProject, keywords: e.target.value })}
            style={styles.input}
          />
          <button type="submit" style={styles.submitBtn}>Create Project</button>
        </form>
      )}

      <div style={styles.grid}>
        {projects.map((project) => (
          <div
            key={project.id}
            style={styles.card}
            onClick={() => router.push(`/projects/${project.id}`)}
          >
            <div style={styles.cardHeader}>
              <h3 style={styles.cardTitle}>{project.name}</h3>
              <span style={{ ...styles.statusDot, background: project.is_active ? "#2ecc71" : "#e74c3c" }} />
            </div>
            <div style={styles.keywords}>
              {project.keywords.map((kw) => (
                <span key={kw} style={styles.keyword}>{kw}</span>
              ))}
            </div>
            <p style={styles.date}>Created {new Date(project.created_at).toLocaleDateString()}</p>
          </div>
        ))}

        {projects.length === 0 && !showCreate && (
          <div style={styles.empty}>
            <p>No projects yet. Create your first project to start mining leads.</p>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" },
  title: { margin: 0, fontSize: "28px", color: "#1a1a2e" },
  createBtn: { padding: "10px 20px", background: "#1a1a2e", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "600" },
  error: { background: "#fee", color: "#c00", padding: "10px 14px", borderRadius: "6px", marginBottom: "16px", fontSize: "14px" },
  createForm: { display: "flex", gap: "12px", marginBottom: "24px", padding: "20px", background: "#fff", borderRadius: "8px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" },
  input: { flex: 1, padding: "10px 12px", border: "1px solid #ddd", borderRadius: "6px", fontSize: "14px" },
  submitBtn: { padding: "10px 20px", background: "#2ecc71", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "600", whiteSpace: "nowrap" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "16px" },
  card: { background: "#fff", padding: "20px", borderRadius: "8px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", cursor: "pointer", transition: "box-shadow 0.2s" },
  cardHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  cardTitle: { margin: "0 0 12px", fontSize: "18px", color: "#1a1a2e" },
  statusDot: { width: "10px", height: "10px", borderRadius: "50%", display: "inline-block" },
  keywords: { display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "12px" },
  keyword: { background: "#e8f4f8", color: "#2980b9", padding: "4px 10px", borderRadius: "12px", fontSize: "12px" },
  date: { margin: 0, color: "#aaa", fontSize: "13px" },
  empty: { gridColumn: "1 / -1", textAlign: "center", padding: "60px 20px", color: "#888" },
};
