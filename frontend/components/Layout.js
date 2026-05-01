import { useAuth } from "../lib/auth";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function Layout({ children }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  const publicPages = ["/login", "/register"];
  const isPublic = publicPages.includes(router.pathname);

  useEffect(() => {
    if (!loading && !user && !isPublic) {
      router.push("/login");
    }
  }, [user, loading, isPublic, router]);

  if (loading) {
    return (
      <div style={styles.loading}>
        <p>Loading...</p>
      </div>
    );
  }

  if (!user && !isPublic) return null;

  return (
    <div style={styles.container}>
      {user && (
        <nav style={styles.nav}>
          <div style={styles.navLeft}>
            <span style={styles.logo} onClick={() => router.push("/dashboard")}>
              Social Intent Miner
            </span>
            <a style={styles.navLink} onClick={() => router.push("/dashboard")}>Dashboard</a>
            <a style={styles.navLink} onClick={() => router.push("/billing")}>Billing</a>
          </div>
          <div style={styles.navRight}>
            <span style={styles.email}>{user.email}</span>
            <button style={styles.logoutBtn} onClick={logout}>Logout</button>
          </div>
        </nav>
      )}
      <main style={styles.main}>{children}</main>
    </div>
  );
}

const styles = {
  container: { minHeight: "100vh", background: "#f5f7fa", fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" },
  loading: { display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" },
  nav: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 24px", background: "#1a1a2e", color: "#fff" },
  navLeft: { display: "flex", alignItems: "center", gap: "24px" },
  navRight: { display: "flex", alignItems: "center", gap: "16px" },
  logo: { fontWeight: "bold", fontSize: "18px", cursor: "pointer" },
  navLink: { color: "#ccc", cursor: "pointer", textDecoration: "none", fontSize: "14px" },
  email: { color: "#888", fontSize: "14px" },
  logoutBtn: { background: "transparent", border: "1px solid #555", color: "#ccc", padding: "6px 12px", borderRadius: "4px", cursor: "pointer" },
  main: { maxWidth: "1200px", margin: "0 auto", padding: "24px" },
};
