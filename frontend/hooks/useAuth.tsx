"use client";

import * as React from "react";
import {
  api,
  getAuthToken,
  setAuthToken,
  setUnauthorizedHandler,
} from "@/lib/api";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const logout = React.useCallback(() => {
    setAuthToken(null);
    setUser(null);
  }, []);

  const login = React.useCallback((token: string, u: User) => {
    setAuthToken(token);
    setUser(u);
  }, []);

  // On mount: if a token exists, hydrate the user from /auth/me.
  React.useEffect(() => {
    setUnauthorizedHandler(() => setUser(null));
    const token = getAuthToken();
    if (!token) {
      setIsLoading(false);
      return;
    }
    api
      .me()
      .then((u) => setUser(u))
      .catch(() => setAuthToken(null))
      .finally(() => setIsLoading(false));
    return () => setUnauthorizedHandler(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
