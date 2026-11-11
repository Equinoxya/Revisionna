import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../lib/AuthContext.jsx";

export default function ProtectedRoute({ children }) {
  const { user, chargement } = useAuth();
  const location = useLocation();

  if (chargement) return <p className="etat">Ouverture du cahier…</p>;
  if (!user) return <Navigate to="/connexion" replace state={{ depuis: location.pathname }} />;
  return children;
}
