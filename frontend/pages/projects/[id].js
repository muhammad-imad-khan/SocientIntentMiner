import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { api } from "../../lib/api";
import LeadTable from "../../components/LeadTable";

export default function ProjectDetailPage() {
  const router = useRouter();
  const { id } = router.query;

  const [project, setProject] = useState(null);
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    if (id) {
      loadProject();
      loadLeads();
      loadStats();
    }
  }, [id, page]);

  const loadProject = async () => {
    try {
      setProject(await api.getProject(id));
    } catch (err) {
      setError(err.message);
    }
  };

  const loadLeads = async () => {
    try {
      const data = await api.getLeads(id, { page, per_page: 25 });
      setLeads(data.leads);
      setTotal(data.total);
    } catch (err) {
      setError(err.message);
    }
  };

  const loadStats = async () => {
    try {
      setStats(await api.getLeadStats(id));
    } catch (err) {
      /* stats are optional */
    }
  };

  const handleStatusChange = async (leadId, status) => {
    try {
      await api.updateLeadStatus(id, leadId, status);
      loadLeads();
    } catch (err) {
      setError(err.message);
    }
  };

  if (!project) return <p>Loading project...</p>;

  const totalPages = Math.ceil(total / 25);

  return (
    <div>
      <button onClick={() => router.push("/dashboard")} style={styles.backBtn}>
        ← Back to Projects
      </button>

      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>{project.name}</h1>
          <div style={styles.keywords}>
            {project.keywords.map((kw) => (
              <span key={kw} style={styles.keyword}>{kw}</span>
            ))}
          </div>
        </div>
      </div>

      {stats && (
        <div style={styles.statsRow}>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{stats.total_leads}</div>
            <div style={styles.statLabel}>Total Leads</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statValue, color: "#2ecc71" }}>{stats.high_intent_leads}</div>
            <div style={styles.statLabel}>High Intent</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statValue, color: "#3498db" }}>
              {(stats.average_intent_score * 100).toFixed(0)}%
            </div>
            <div style={styles.statLabel}>Avg Score</div>
          </div>
        </div>
      )}

      {error && <div style={styles.error}>{error}</div>}

      <LeadTable leads={leads} onStatusChange={handleStatusChange} />

      {totalPages > 1 && (
        <div style={styles.pagination}>
          <button
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
            style={styles.pageBtn}
          >
            Previous
          </button>
          <span style={styles.pageInfo}>Page {page} of {totalPages}</span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
            style={styles.pageBtn}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

const styles = {
  backBtn: { background: "none", border: "none", color: "#888", cursor: "pointer", fontSize: "14px", padding: "0", marginBottom: "16px" },
  header: { marginBottom: "24px" },
  title: { margin: "0 0 8px", fontSize: "28px", color: "#1a1a2e" },
  keywords: { display: "flex", flexWrap: "wrap", gap: "6px" },
  keyword: { background: "#e8f4f8", color: "#2980b9", padding: "4px 10px", borderRadius: "12px", fontSize: "12px" },
  statsRow: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "24px" },
  statCard: { background: "#fff", padding: "20px", borderRadius: "8px", textAlign: "center", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" },
  statValue: { fontSize: "32px", fontWeight: "bold", color: "#1a1a2e" },
  statLabel: { fontSize: "13px", color: "#888", marginTop: "4px" },
  error: { background: "#fee", color: "#c00", padding: "10px 14px", borderRadius: "6px", marginBottom: "16px", fontSize: "14px" },
  pagination: { display: "flex", justifyContent: "center", alignItems: "center", gap: "16px", marginTop: "24px" },
  pageBtn: { padding: "8px 16px", border: "1px solid #ddd", borderRadius: "6px", background: "#fff", cursor: "pointer" },
  pageInfo: { color: "#888", fontSize: "14px" },
};
