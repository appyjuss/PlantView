import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function SignUp() {
	const [name, setName] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const { signup } = useAuth();
	const navigate = useNavigate();

	const submit = async (e: React.FormEvent) => {
		e.preventDefault();
		try {
			await signup(name, email, password);
			navigate("/dashboard", { replace: true });
		} catch (err) {
			console.error(err);
		}
	};

	return (
		<div className="max-w-md mx-auto mt-12 p-6 bg-white rounded-lg shadow">
			<h2 className="text-2xl font-semibold mb-4">Create account</h2>
			<form onSubmit={submit} className="flex flex-col gap-4">
				<input className="border p-3 rounded" placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} />
				<input className="border p-3 rounded" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
				<input className="border p-3 rounded" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
				<button className="bg-emerald-600 text-white px-4 py-2 rounded">Create account</button>
			</form>

			<p className="mt-4 text-sm">
				Already have an account? <Link to="/login" className="text-emerald-600">Sign in</Link>
			</p>
		</div>
	);
}
