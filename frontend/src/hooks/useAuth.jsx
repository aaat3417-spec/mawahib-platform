import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("mawahib_user");
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("mawahib_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/auth/me")
      .then(({ data }) => {
        setUser(data);
        localStorage.setItem("mawahib_user", JSON.stringify(data));
      })
      .catch(() => {
        localStorage.removeItem("mawahib_token");
        localStorage.removeItem("mawahib_user");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const form = new FormData();
    form.append("username", email);
    form.append("password", password);
    const { data } = await api.post("/auth/login", form);
    localStorage.setItem("mawahib_token", data.access_token);
    const me = await api.get("/auth/me");
    setUser(me.data);
    localStorage.setItem("mawahib_user", JSON.stringify(me.data));
    return me.data;
  }

  async function setupOwner(payload) {
    const { data } = await api.post("/auth/setup-owner", payload);
    localStorage.setItem("mawahib_token", data.access_token);
    const me = await api.get("/auth/me");
    setUser(me.data);
    localStorage.setItem("mawahib_user", JSON.stringify(me.data));
    return me.data;
  }

  function logout() {
    localStorage.removeItem("mawahib_token");
    localStorage.removeItem("mawahib_user");
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      setupOwner,
      logout,
      isAdmin: user?.role === "owner" || user?.role === "admin",
      isLeader: user?.role === "team_leader",
      canReview: ["owner", "admin", "team_leader"].includes(user?.role)
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}

