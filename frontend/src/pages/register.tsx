import { useState } from "react";
import { useRouter } from "next/router";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    const res = await fetch("https://01355a92bff5.ngrok-free.app/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (res.ok) {
      setSuccess("Registration successful! You can now login.");
      setTimeout(() => router.push("/login"), 1500);
    } else {
      setError(data.detail || "Registration failed");
    }
  }

  return (
    <div className="container auth-container">
      <h2 className="auth-title">Create Account</h2>
      <form className="auth-form" onSubmit={handleRegister}>
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
        <button type="submit" className="auth-btn">Register</button>
      </form>
      {error && <p className="error auth-error">{error}</p>}
      {success && <p className="auth-success">{success}</p>}
      <p className="auth-link">
        Already have an account? <a href="/login">Login</a>
      </p>
    </div>
  );
}
