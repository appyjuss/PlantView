import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import PrivateRoute from "./components/PrivateRoute";
import "./App.css";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="app-root">
          <main className="app-main">
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <Dashboard />
                  </PrivateRoute>
                }
              />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
              {/* add more routes here */}
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
