import React, { createContext, useContext, useEffect, useState } from "react";
import { 
  signup as apiSignup, 
  login as apiLogin, 
  verifyToken, 
  setToken, 
  setRefreshToken,
  getToken, 
  clearTokens,
  logout as apiLogout 
} from "../lib/api";

type User = {
  id: string;
  email: string;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // On mount, check if user is still authenticated with the backend
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = getToken();
        if (token) {
          const { user } = await verifyToken();
          setUser(user);
        }
      } catch (error) {
        // Auth initialization error - clearing tokens
        clearTokens();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const { access_token, refresh_token, user } = await apiLogin(email, password);
      setToken(access_token);
      setRefreshToken(refresh_token);
      setUser(user);
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email: string, password: string) => {
    setLoading(true);
    try {
      const { access_token, refresh_token, user } = await apiSignup(email, password);
      setToken(access_token);
      setRefreshToken(refresh_token);
      setUser(user);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch (error) {
      // Logout error ignored
    } finally {
      clearTokens();
      setUser(null);
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
