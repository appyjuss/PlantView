import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { apiFetch, registerAuthHandlers, API_BASE } from "../lib/api";

type User = {
  id: string;
  name: string;
  email: string;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  login: (email: string, password?: string) => Promise<void>;
  signup: (name: string, email: string, password?: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // On mount, check if user is still authenticated with the backend
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const resp = await apiFetch(`${API_BASE}/current-user`, { method: "GET" });
        if (resp.ok) {
          const data = await resp.json();
          if (data.user) setUser(data.user);
        }
      } catch (e) {
        // not authenticated or error; proceed with no user
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (email: string, password: string = "password") => {
    setLoading(true);
    try {
      const resp = await apiFetch(`${API_BASE}/login`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.user) setUser(data.user);
      } else {
        throw new Error(`Login failed: ${resp.statusText}`);
      }
    } catch (err) {
      console.error("Login error:", err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (_name: string, email: string, password: string = "password") => {
    // For now, reuse login. In a real app you'd POST to /API/signup
    return login(email, password);
  };

  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await apiFetch(`${API_BASE}/logout`, { method: 'POST' });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
      try {
        localStorage.removeItem('mock_user');
        sessionStorage.removeItem('mock_user');
      } catch (e) {}
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(async (): Promise<boolean> => {
    try {
      const resp = await fetch(`${API_BASE}/refresh`, { method: 'POST', credentials: 'include' });
      if (!resp.ok) return false;
      const data = await resp.json();
      if (data.user) {
        setUser(data.user);
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }, []);

  // register auth handlers so apiFetch can call refresh and logout when needed
  useEffect(() => {
    registerAuthHandlers({ refresh, logout });
  }, [refresh, logout]);

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};

export default AuthContext;
