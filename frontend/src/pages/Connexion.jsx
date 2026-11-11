import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../lib/AuthContext.jsx";

export default function Connexion() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [identifiant, setIdentifiant] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState(null);
  const [envoi, setEnvoi] = useState(false);

  async function soumettre(evenement) {
    evenement.preventDefault();
    setErreur(null);
    setEnvoi(true);
    try {
      await login(identifiant, motDePasse);
      navigate(location.state?.from || "/", { replace: true });
    } catch (exception) {
      setErreur(exception.message);
    } finally {
      setEnvoi(false);
    }
  }

  return (
    <div className="page-auth">
      <form className="carte-auth" onSubmit={soumettre}>
        <h1>
          <span aria-hidden="true">📚</span> Revisionna
        </h1>
        <p className="sous-titre">Connectez-vous pour reprendre vos revisions.</p>

        {erreur && <p className="alerte">{erreur}</p>}

        <label htmlFor="identifiant">Email ou nom d&apos;utilisateur</label>
        <input
          id="identifiant"
          autoComplete="username"
          value={identifiant}
          onChange={(e) => setIdentifiant(e.target.value)}
          required
        />

        <label htmlFor="motdepasse">Mot de passe</label>
        <input
          id="motdepasse"
          type="password"
          autoComplete="current-password"
          value={motDePasse}
          onChange={(e) => setMotDePasse(e.target.value)}
          required
        />

        <button type="submit" className="bouton" disabled={envoi}>
          {envoi ? "Connexion..." : "Se connecter"}
        </button>

        <p className="bascule">
          Pas encore de compte ? <Link to="/inscription">Creer un compte</Link>
        </p>
      </form>
    </div>
  );
}
