import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import Champ from "../components/Champ.jsx";
import Couverture from "../components/Couverture.jsx";
import { useAuth } from "../lib/AuthContext.jsx";

export default function Connexion() {
  const { user, login, expiree } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const destination = location.state?.depuis || "/";

  const [identifiant, setIdentifiant] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState(null);
  const [envoi, setEnvoi] = useState(false);

  if (user) return <Navigate to={destination} replace />;

  async function soumettre(evenement) {
    evenement.preventDefault();
    setErreur(null);
    setEnvoi(true);
    try {
      await login(identifiant, motDePasse);
      navigate(destination, { replace: true });
    } catch (exception) {
      setErreur(exception.message);
      setEnvoi(false);
    }
  }

  return (
    <Couverture>
      <form onSubmit={soumettre} noValidate>
        <h1>Se connecter</h1>
        <p className="chapeau">Reprenez là où vous vous étiez arrêté.</p>

        {expiree && !erreur && (
          <div className="message" role="status">
            <p>Votre session a pris fin. Reconnectez-vous pour continuer.</p>
          </div>
        )}
        {erreur && (
          <div className="message erreur" role="alert">
            <p>{erreur}</p>
          </div>
        )}

        <Champ
          libelle="Email ou nom d'utilisateur"
          autoComplete="username"
          autoCapitalize="none"
          spellCheck="false"
          value={identifiant}
          onChange={(e) => setIdentifiant(e.target.value)}
          required
        />
        <Champ
          libelle="Mot de passe"
          type="password"
          autoComplete="current-password"
          value={motDePasse}
          onChange={(e) => setMotDePasse(e.target.value)}
          required
        />

        <button type="submit" className="bouton" disabled={envoi || !identifiant || !motDePasse}>
          {envoi ? "Connexion…" : "Ouvrir mon cahier"}
        </button>

        <p className="bascule">
          Pas encore de compte ? <Link to="/inscription">Créer un compte</Link>
        </p>
        <p className="aide discret">
          Mot de passe oublié ? Demandez à la personne qui administre ce site de le réinitialiser.
        </p>
      </form>
    </Couverture>
  );
}
