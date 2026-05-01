import { useState } from "react";
import { useRouter } from "next/router";
import { useAuth } from "../lib/auth";

export default function RegisterPage() {
  const [form, setForm] = useState({ email: "", password: "", full_name: "", organization_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      router.push("/dashboard");
    } catch (err) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <h1 style={styles.title}>Create Account</h1>
        <p style={styles.subtitle}>Start finding high-intent leads</p>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>Full Name</label>
            <input type="text" required value={form.full_name} onChange={update("full_name")} style={styles.input} placeholder="Jane Smith" />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Company / Organization</label>
            <input type="text" required value={form.organization_name} onChange={update("organization_name")} style={styles.input} placeholder="Acme Corp" />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input type="email" required value={form.email} onChange={update("email")} style={styles.input} placeholder="you@example.com" />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input type="password" required minLength={8} value={form.password} onChange={update("password")} style={styles.input} placeholder="Min 8 characters" />
          </div>

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p style={styles.switch}>
          Already have an account?{" "}
          <a onClick={() => router.push("/login")} style={styles.link}>Sign in</a>
        </p>
      </div>
    </div>
  );
}

const styles = {
  wrapper: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "80vh" },
  card: { background: "#fff", padding: "40px", borderRadius: "12px", boxShadow: "0 4px 24px rgba(0,0,0,0.08)", width: "100%", maxWidth: "440px" },
  title: { margin: "0 0 4px", fontSize: "24px", color: "#1a1a2e" },
  subtitle: { margin: "0 0 24px", color: "#888", fontSize: "14px" },
  error: { background: "#fee", color: "#c00", padding: "10px 14px", borderRadius: "6px", marginBottom: "16px", fontSize: "14px" },
  field: { marginBottom: "16px" },
  label: { display: "block", marginBottom: "6px", fontSize: "14px", fontWeight: "500", color: "#333" },
  input: { width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: "6px", fontSize: "14px", boxSizing: "border-box" },
  button: { width: "100%", padding: "12px", background: "#1a1a2e", color: "#fff", border: "none", borderRadius: "6px", fontSize: "15px", fontWeight: "600", cursor: "pointer" },
  switch: { textAlign: "center", marginTop: "20px", fontSize: "14px", color: "#888" },
  link: { color: "#1a1a2e", fontWeight: "600", cursor: "pointer" },
};
