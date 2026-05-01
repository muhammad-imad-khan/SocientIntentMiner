import { useState, useEffect } from "react";
import { api } from "../lib/api";

export default function BillingPage() {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadSubscription();
  }, []);

  const loadSubscription = async () => {
    try {
      setSubscription(await api.getSubscription());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async () => {
    try {
      const { checkout_url } = await api.createCheckout({
        price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_PRO || "",
        success_url: window.location.origin + "/billing?success=true",
        cancel_url: window.location.origin + "/billing",
      });
      window.location.href = checkout_url;
    } catch (err) {
      setError(err.message);
    }
  };

  const handleManage = async () => {
    try {
      const { url } = await api.createPortal();
      window.location.href = url;
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1 style={styles.title}>Billing & Subscription</h1>

      {error && <div style={styles.error}>{error}</div>}

      {subscription && (
        <div style={styles.grid}>
          {/* Current Plan */}
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>Current Plan</h3>
            <div style={styles.planBadge}>{subscription.plan.toUpperCase()}</div>
            <div style={styles.limits}>
              <div style={styles.limitRow}>
                <span>Max Projects</span>
                <strong>{subscription.max_projects}</strong>
              </div>
              <div style={styles.limitRow}>
                <span>Leads per Day</span>
                <strong>{subscription.max_leads_per_day}</strong>
              </div>
            </div>
            {subscription.plan === "free" ? (
              <button style={styles.upgradeBtn} onClick={handleUpgrade}>
                Upgrade to Pro
              </button>
            ) : (
              <button style={styles.manageBtn} onClick={handleManage}>
                Manage Subscription
              </button>
            )}
          </div>

          {/* Plans Comparison */}
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>Plans</h3>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Feature</th>
                  <th style={styles.th}>Free</th>
                  <th style={styles.th}>Pro</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={styles.td}>Projects</td>
                  <td style={styles.td}>1</td>
                  <td style={styles.td}>10</td>
                </tr>
                <tr>
                  <td style={styles.td}>Leads / Day</td>
                  <td style={styles.td}>50</td>
                  <td style={styles.td}>1,000</td>
                </tr>
                <tr>
                  <td style={styles.td}>Intent Scoring</td>
                  <td style={styles.td}>Basic</td>
                  <td style={styles.td}>Advanced</td>
                </tr>
                <tr>
                  <td style={styles.td}>Auto-scraping</td>
                  <td style={styles.td}>Manual</td>
                  <td style={styles.td}>Every 6h</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  title: { margin: "0 0 24px", fontSize: "28px", color: "#1a1a2e" },
  error: { background: "#fee", color: "#c00", padding: "10px 14px", borderRadius: "6px", marginBottom: "16px", fontSize: "14px" },
  grid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" },
  card: { background: "#fff", padding: "24px", borderRadius: "8px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" },
  cardTitle: { margin: "0 0 16px", fontSize: "18px", color: "#1a1a2e" },
  planBadge: { display: "inline-block", padding: "6px 16px", background: "#e8f4f8", color: "#2980b9", borderRadius: "16px", fontWeight: "bold", fontSize: "14px", marginBottom: "20px" },
  limits: { marginBottom: "20px" },
  limitRow: { display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f0f0f0", fontSize: "14px" },
  upgradeBtn: { width: "100%", padding: "12px", background: "#2ecc71", color: "#fff", border: "none", borderRadius: "6px", fontSize: "15px", fontWeight: "600", cursor: "pointer" },
  manageBtn: { width: "100%", padding: "12px", background: "#3498db", color: "#fff", border: "none", borderRadius: "6px", fontSize: "15px", fontWeight: "600", cursor: "pointer" },
  table: { width: "100%", borderCollapse: "collapse" },
  th: { textAlign: "left", padding: "10px 12px", borderBottom: "2px solid #e9ecef", fontSize: "13px", color: "#666" },
  td: { padding: "10px 12px", borderBottom: "1px solid #f0f0f0", fontSize: "14px" },
};
