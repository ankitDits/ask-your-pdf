import { useState } from "react";
import { useRouter } from "next/router";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const res = await fetch("https://01355a92bff5.ngrok-free.app/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("token", data.access_token);
      // Decode JWT to get user_id
      try {
        const payload = JSON.parse(atob(data.access_token.split('.')[1]));
        if (payload.user_id) {
          localStorage.setItem("user_id", payload.user_id);
        }
      } catch {}
      router.push("/dashboard");
    } else {
      setError(data.detail || "Login failed");
    }
  }

  return (
    <div className="container auth-container">
      <h2 className="auth-title">Login</h2>
      <form className="auth-form" onSubmit={handleLogin}>
        <input
          type="text"
          className="auth-input"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          className="auth-input"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button type="submit" className="auth-btn">Login</button>
      </form>
      {error && <p className="error auth-error">{error}</p>}
      <p className="auth-link">
        Don't have an account? <a href="/register">Register</a>
      </p>
    </div>
  );
}
