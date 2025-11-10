import { BrowserRouter, Routes, Route} from "react-router-dom";
// import { AuthProvider, useAuth } from "./context/AuthContext";
// import Nav from "./components/Nav";
import Landing from "./pages/Landing.tsx";
// import Dashboard from "./pages/Dashboard";
// import Login from "./pages/Login";
import "./App.css";

// function PrivateRoute({ children }: { children: JSX.Element }) {
//   const { user } = useAuth();
//   if (!user) return <Navigate to="/login" replace />;
//   return children;
// }

export default function App() {
  return (
    // <AuthProvider>
      <BrowserRouter>
        <div className="app-root">
          {/* <Nav /> */}
          <main className="app-main">
            <Routes>
              <Route path="/" element={<Landing />} />
              {/* <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <Dashboard />
                  </PrivateRoute>
                }
              />
              <Route path="/login" element={<Login />} /> */}
              {/* add more routes here */}
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    // </AuthProvider>
  );
}
