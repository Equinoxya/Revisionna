import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api, hasSession, SESSION_EXPIRED } from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [chargement, setChargement] = useState(hasSession());
  const [expiree, setExpiree] = useState(false);

  // Au démarrage : s'il semble y avoir une session, on demande au serveur qui on est.
  useEffect(() => {
    if (!hasSession()) return undefined;
    let annule = false;
    api("/auth/me")
      .then((data) => {
        if (!annule) setUser(data.user);
      })
      .catch(() => {
        if (!annule) setUser(null);
      })
      .finally(() => {
        if (!annule) setChargement(false);
      });
    return () => {
      annule = true;
    };
  }, []);

  // Le serveur a refusé la session (expirée, fermée ailleurs) : retour à la connexion.
  useEffect(() => {
    function fermer() {
      setUser((actuel) => {
        if (actuel) setExpiree(true);
        return null;
      });
    }
    window.addEventListener(SESSION_EXPIRED, fermer);
    return () => window.removeEventListener(SESSION_EXPIRED, fermer);
  }, []);

  const login = useCallback(async (identifier, password) => {
    const data = await api("/auth/login", { method: "POST", body: { identifier, password } });
    setExpiree(false);
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (champs) => {
    const data = await api("/auth/register", { method: "POST", body: champs });
    setExpiree(false);
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await api("/auth/logout", { method: "POST" });
    } catch {
      // Même si le serveur ne répond pas, on quitte l'espace connecté.
    }
    setUser(null);
  }, []);

  const valeur = useMemo(
    () => ({ user, setUser, chargement, expiree, login, register, logout }),
    [user, chargement, expiree, login, register, logout],
  );

  return <AuthContext.Provider value={valeur}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const contexte = useContext(AuthContext);
  if (!contexte) throw new Error("useAuth doit être utilisé dans un AuthProvider");
  return contexte;
}
