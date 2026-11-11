import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../lib/AuthContext.jsx";

export default function Inscription() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [champs, setChamps] = useState({ email: "", username: "", password: "" });
  const [erreurs, setErreurs] = useState({});
  const [erreur, setErreur] = useState(null);
  const [envoi, setEnvoi] = useState(false);

  function modifier(nom) {
    return (evenement) => setChamps({ ...champs, [nom]: evenement.target.value });
  }

  async function soumettre(evenement) {
    evenement.preventDefault();
    setErreur(null);
    setErreurs({});
    setEnvoi(true);
    try {
      await register(champs.email, champs.username, champs.password);
      navigate("/", { replace: true });
    } catch (exception) {
      setErreurs(exception.payload?.errors || {});
      if (!exception.payload?.errors) setErreur(exception.message);
    } finally {
      setEnvoi(false);
    }
  }

  return (
    <div className="page-auth">
      <form className="carte-auth" onSubmit={soumettre}>
        <h1>Creer un compte</h1>
        <p className="sous-titre">11 cours, des lecons interactives et des TP corriges.</p>

        {erreur && <p className="alerte">{erreur}</p>}

        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={champs.email} onChange={modifier("email")} required />
        {erreurs.email && <small className="champ-erreur">{erreurs.email}</small>}

        <label htmlFor="username">Nom d&apos;utilisateur</label>
        <input id="username" value={champs.username} onChange={modifier("username")} required />
        {erreurs.username && <small className="champ-erreur">{erreurs.username}</small>}

        <label htmlFor="password">Mot de passe (8 caracteres minimum)</label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          value={champs.password}
          onChange={modifier("password")}
          required
        />
        {erreurs.password && <small className="champ-erreur">{erreurs.password}</small>}

        <button type="submit" className="bouton" disabled={envoi}>
          {envoi ? "Creation..." : "Creer mon compte"}
        </button>

        <p className="bascule">
          Deja inscrit ? <Link to="/connexion">Se connecter</Link>
        </p>
      </form>
    </div>
  );
}
