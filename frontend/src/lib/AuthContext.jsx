import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api, getToken, setToken } from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [chargement, setChargement] = useState(Boolean(getToken()));

  // Au montage : si un jeton existe, on verifie qu'il est encore valide.
  useEffect(() => {
    let annule = false;
    if (!getToken()) {
      setChargement(false);
      return undefined;
    }
    api("/auth/me")
      .then((data) => {
        if (!annule) setUser(data.user);
      })
      .catch(() => {
        setToken(null);
        if (!annule) setUser(null);
      })
      .finally(() => {
        if (!annule) setChargement(false);
      });
    return () => {
      annule = true;
    };
  }, []);

  const login = useCallback(async (identifiant, motDePasse) => {
    const data = await api("/auth/login", {
      method: "POST",
      auth: false,
      body: { email: identifiant, password: motDePasse },
    });
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (email, username, motDePasse) => {
    const data = await api("/auth/register", {
      method: "POST",
      auth: false,
      body: { email, username, password: motDePasse },
    });
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await api("/auth/logout", { method: "POST" });
    } catch {
      /* jeton deja expire : on nettoie quand meme */
    }
    setToken(null);
    setUser(null);
  }, []);

  const valeur = useMemo(
    () => ({ user, chargement, login, register, logout }),
    [user, chargement, login, register, logout],
  );

  return <AuthContext.Provider value={valeur}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const contexte = useContext(AuthContext);
  if (!contexte) throw new Error("useAuth doit etre utilise dans un AuthProvider");
  return contexte;
}
