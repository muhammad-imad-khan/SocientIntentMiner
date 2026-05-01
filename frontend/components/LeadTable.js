const STATUS_COLORS = {
  new: "#3498db",
  contacted: "#f39c12",
  qualified: "#2ecc71",
  converted: "#27ae60",
  dismissed: "#95a5a6",
};

export default function LeadTable({ leads, onStatusChange }) {
  if (!leads || leads.length === 0) {
    return <p style={{ color: "#888", textAlign: "center", padding: "40px" }}>No leads found.</p>;
  }

  return (
    <table style={styles.table}>
      <thead>
        <tr>
          <th style={styles.th}>Score</th>
          <th style={styles.th}>Author</th>
          <th style={styles.th}>Content</th>
          <th style={styles.th}>Platform</th>
          <th style={styles.th}>Status</th>
          <th style={styles.th}>Actions</th>
        </tr>
      </thead>
      <tbody>
        {leads.map((lead) => (
          <tr key={lead.id} style={styles.tr}>
            <td style={styles.td}>
              <span style={{
                ...styles.scoreBadge,
                background: lead.intent_score >= 0.7 ? "#2ecc71" : lead.intent_score >= 0.4 ? "#f39c12" : "#e74c3c",
              }}>
                {(lead.intent_score * 100).toFixed(0)}%
              </span>
            </td>
            <td style={styles.td}>{lead.author_handle}</td>
            <td style={{ ...styles.td, maxWidth: "400px" }}>
              <a href={lead.url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                {lead.content.length > 120 ? lead.content.slice(0, 120) + "..." : lead.content}
              </a>
            </td>
            <td style={styles.td}>{lead.platform}</td>
            <td style={styles.td}>
              <span style={{ ...styles.statusBadge, background: STATUS_COLORS[lead.status] || "#888" }}>
                {lead.status}
              </span>
            </td>
            <td style={styles.td}>
              <select
                value={lead.status}
                onChange={(e) => onStatusChange(lead.id, e.target.value)}
                style={styles.select}
              >
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="qualified">Qualified</option>
                <option value="converted">Converted</option>
                <option value="dismissed">Dismissed</option>
              </select>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const styles = {
  table: { width: "100%", borderCollapse: "collapse", background: "#fff", borderRadius: "8px", overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" },
  th: { textAlign: "left", padding: "12px 16px", background: "#f8f9fa", borderBottom: "2px solid #e9ecef", fontSize: "13px", color: "#666", fontWeight: "600" },
  tr: { borderBottom: "1px solid #f0f0f0" },
  td: { padding: "12px 16px", fontSize: "14px" },
  scoreBadge: { display: "inline-block", padding: "4px 10px", borderRadius: "12px", color: "#fff", fontWeight: "bold", fontSize: "12px" },
  statusBadge: { display: "inline-block", padding: "4px 10px", borderRadius: "12px", color: "#fff", fontSize: "12px", textTransform: "capitalize" },
  link: { color: "#2c3e50", textDecoration: "none" },
  select: { padding: "6px 8px", borderRadius: "4px", border: "1px solid #ddd", fontSize: "13px" },
};
