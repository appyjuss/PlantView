import React, { useState } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || "/dashboard";

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-12 p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-semibold mb-4">Sign in</h2>
      <form onSubmit={submit} className="flex flex-col gap-4">
        <input className="border p-3 rounded" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="border p-3 rounded" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button className="bg-emerald-600 text-white px-4 py-2 rounded">Sign in</button>
      </form>

      <p className="mt-4 text-sm">
        Don't have an account? <Link to="/signup" className="text-emerald-600">Sign up</Link>
      </p>
    </div>
  );
}
