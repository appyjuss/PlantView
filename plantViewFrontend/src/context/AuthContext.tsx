import React, { createContext, useContext, useEffect, useState } from "react";

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
        const resp = await fetch("/API/current-user", {
          method: "GET",
          credentials: "include",
        });
        if (resp.ok) {
          const data = await resp.json();
          if (data.user) {
            setUser(data.user);
          }
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
      const resp = await fetch("/API/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.user) {
          setUser(data.user);
        }
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

  const signup = async (name: string, email: string, password: string = "password") => {
    setLoading(true);
    try {
      // For now, signup just calls login with the provided info
      // In a real app, you'd call a /API/signup endpoint that validates and creates a new user
      const resp = await fetch("/API/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.user) {
          setUser(data.user);
        }
      } else {
        throw new Error(`Signup failed: ${resp.statusText}`);
      }
    } catch (err) {
      console.error("Signup error:", err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await fetch("/API/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      setUser(null);
      setLoading(false);
    }
  };

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
