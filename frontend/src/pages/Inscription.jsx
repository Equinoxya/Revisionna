import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import Champ from "../components/Champ.jsx";
import Couverture from "../components/Couverture.jsx";
import { useAuth } from "../lib/AuthContext.jsx";
import { useMeta } from "../lib/meta.js";

export default function Inscription() {
  const { user, register } = useAuth();
  const meta = useMeta();
  const navigate = useNavigate();

  const [champs, setChamps] = useState({ email: "", username: "", password: "", invite_code: "" });
  const [accepte, setAccepte] = useState(false);
  const [erreurs, setErreurs] = useState({});
  const [erreur, setErreur] = useState(null);
  const [envoi, setEnvoi] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const modifier = (nom) => (evenement) => setChamps({ ...champs, [nom]: evenement.target.value });

  const mdp = champs.password;
  const criteres = [
    { texte: `${meta.password_min_length} caractères`, rempli: mdp.length >= meta.password_min_length },
    { texte: "une lettre", rempli: /\p{L}/u.test(mdp) },
    { texte: "un chiffre", rempli: /\d/.test(mdp) },
  ];

  async function soumettre(evenement) {
    evenement.preventDefault();
    setErreur(null);
    setErreurs({});
    setEnvoi(true);
    try {
      await register({ ...champs, accept_terms: accepte });
      navigate("/", { replace: true });
    } catch (exception) {
      if (Object.keys(exception.fields).length) setErreurs(exception.fields);
      else setErreur(exception.message);
      setEnvoi(false);
    }
  }

  return (
    <Couverture>
      <form onSubmit={soumettre} noValidate>
        <h1>Créer un compte</h1>
        <p className="chapeau">Trois informations, pas une de plus.</p>

        {erreur && (
          <div className="message erreur" role="alert">
            <p>{erreur}</p>
          </div>
        )}

        <Champ
          libelle="Email"
          type="email"
          autoComplete="email"
          value={champs.email}
          onChange={modifier("email")}
          erreur={erreurs.email}
          aide="Il sert d'identifiant. Aucun message ne vous sera envoyé."
          required
        />
        <Champ
          libelle="Nom d'utilisateur"
          autoComplete="username"
          autoCapitalize="none"
          spellCheck="false"
          value={champs.username}
          onChange={modifier("username")}
          erreur={erreurs.username}
          aide="Affiché en haut de votre bulletin."
          required
        />
        <Champ
          libelle="Mot de passe"
          type="password"
          autoComplete="new-password"
          value={champs.password}
          onChange={modifier("password")}
          erreur={erreurs.password}
          required
        >
          <ul className="criteres" aria-label="Le mot de passe doit contenir">
            {criteres.map((critere) => (
              <li key={critere.texte} className={critere.rempli ? "rempli" : undefined}>
                <span className="puce" aria-hidden="true" />
                {critere.texte}
                <span className="sr-only">{critere.rempli ? " : oui" : " : pas encore"}</span>
              </li>
            ))}
          </ul>
        </Champ>

        {meta.invite_required && (
          <Champ
            libelle="Code d'invitation"
            autoComplete="off"
            autoCapitalize="none"
            spellCheck="false"
            value={champs.invite_code}
            onChange={modifier("invite_code")}
            erreur={erreurs.invite_code}
            aide="Communiqué par la personne qui administre ce site."
            required
          />
        )}

        <label className="case">
          <input
            type="checkbox"
            checked={accepte}
            onChange={(e) => setAccepte(e.target.checked)}
            aria-invalid={erreurs.accept_terms ? "true" : undefined}
          />
          <span>
            J&apos;accepte les{" "}
            <Link to="/cgu" target="_blank" rel="noopener">
              conditions d&apos;utilisation
            </Link>{" "}
            et j&apos;ai lu la{" "}
            <Link to="/confidentialite" target="_blank" rel="noopener">
              politique de confidentialité
            </Link>
            .
            {erreurs.accept_terms && (
              <span className="erreur" role="alert">
                {" "}
                {erreurs.accept_terms}
              </span>
            )}
          </span>
        </label>

        <button type="submit" className="bouton" disabled={envoi}>
          {envoi ? "Création…" : "Créer mon compte"}
        </button>

        <p className="bascule">
          Déjà inscrit ? <Link to="/connexion">Se connecter</Link>
        </p>
      </form>
    </Couverture>
  );
}
