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
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("mock_user");
      if (raw) setUser(JSON.parse(raw));
    } catch (e) {
      // ignore
    }
    setLoading(false);
  }, []);

  const login = async (email: string) => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 500));
    const mockUser = { id: "1", name: "Demo User", email };
    localStorage.setItem("mock_user", JSON.stringify(mockUser));
    setUser(mockUser);
    setLoading(false);
  };

  const signup = async (name: string, email: string) => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 600));
    const mockUser = { id: String(Date.now()), name, email };
    localStorage.setItem("mock_user", JSON.stringify(mockUser));
    setUser(mockUser);
    setLoading(false);
  };

  const logout = () => {
    localStorage.removeItem("mock_user");
    setUser(null);
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
