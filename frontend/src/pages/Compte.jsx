import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Champ from "../components/Champ.jsx";
import Icon from "../components/Icon.jsx";
import { api } from "../lib/api.js";
import { useAuth } from "../lib/AuthContext.jsx";
import { useMeta } from "../lib/meta.js";
import { useTheme } from "../lib/theme.jsx";

/** État commun aux petits formulaires de cette page. */
function useFormulaire() {
  const [envoi, setEnvoi] = useState(false);
  const [erreurs, setErreurs] = useState({});
  const [erreur, setErreur] = useState(null);
  const [succes, setSucces] = useState(null);

  async function envoyer(action, messageSucces) {
    setEnvoi(true);
    setErreurs({});
    setErreur(null);
    setSucces(null);
    try {
      await action();
      setSucces(messageSucces);
      return true;
    } catch (exception) {
      if (Object.keys(exception.fields ?? {}).length) setErreurs(exception.fields);
      else setErreur(exception.message);
      return false;
    } finally {
      setEnvoi(false);
    }
  }

  return { envoi, erreurs, erreur, succes, envoyer };
}

function Retours({ formulaire }) {
  return (
    <div aria-live="polite">
      {formulaire.erreur && <p className="message erreur">{formulaire.erreur}</p>}
      {formulaire.succes && <p className="message succes">{formulaire.succes}</p>}
    </div>
  );
}

function Profil() {
  const { user, setUser } = useAuth();
  const formulaire = useFormulaire();
  const [email, setEmail] = useState(user.email);
  const [username, setUsername] = useState(user.username);
  const [motDePasse, setMotDePasse] = useState("");

  async function soumettre(evenement) {
    evenement.preventDefault();
    const ok = await formulaire.envoyer(async () => {
      const data = await api("/me", {
        method: "PATCH",
        body: { email, username, current_password: motDePasse },
      });
      setUser(data.user);
    }, "Profil mis à jour.");
    if (ok) setMotDePasse("");
  }

  return (
    <form onSubmit={soumettre} noValidate>
      <Champ
        libelle="Email"
        type="email"
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        erreur={formulaire.erreurs.email}
      />
      <Champ
        libelle="Nom d'utilisateur"
        autoComplete="username"
        autoCapitalize="none"
        spellCheck="false"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        erreur={formulaire.erreurs.username}
      />
      <Champ
        libelle="Mot de passe actuel"
        type="password"
        autoComplete="current-password"
        value={motDePasse}
        onChange={(e) => setMotDePasse(e.target.value)}
        erreur={formulaire.erreurs.current_password}
        aide="Demandé pour confirmer que c'est bien vous."
      />
      <Retours formulaire={formulaire} />
      <button type="submit" className="bouton-2" disabled={formulaire.envoi || !motDePasse}>
        Enregistrer
      </button>
    </form>
  );
}

function MotDePasse() {
  const meta = useMeta();
  const formulaire = useFormulaire();
  const [actuel, setActuel] = useState("");
  const [nouveau, setNouveau] = useState("");

  async function soumettre(evenement) {
    evenement.preventDefault();
    const ok = await formulaire.envoyer(
      () => api("/auth/password", { method: "POST", body: { current_password: actuel, new_password: nouveau } }),
      "Mot de passe modifié. Vos autres appareils ont été déconnectés.",
    );
    if (ok) {
      setActuel("");
      setNouveau("");
    }
  }

  return (
    <form onSubmit={soumettre} noValidate>
      <Champ
        libelle="Mot de passe actuel"
        type="password"
        autoComplete="current-password"
        value={actuel}
        onChange={(e) => setActuel(e.target.value)}
        erreur={formulaire.erreurs.current_password}
      />
      <Champ
        libelle="Nouveau mot de passe"
        type="password"
        autoComplete="new-password"
        value={nouveau}
        onChange={(e) => setNouveau(e.target.value)}
        erreur={formulaire.erreurs.new_password}
        aide={`${meta.password_min_length} caractères au moins, dont une lettre et un chiffre.`}
      />
      <Retours formulaire={formulaire} />
      <button type="submit" className="bouton-2" disabled={formulaire.envoi || !actuel || !nouveau}>
        Changer de mot de passe
      </button>
    </form>
  );
}

function Apparence() {
  const { choix, setChoix } = useTheme();
  const options = [
    { valeur: "light", libelle: "Cahier (clair)" },
    { valeur: "dark", libelle: "Tableau noir (sombre)" },
    { valeur: "auto", libelle: "Comme mon appareil" },
  ];
  return (
    <fieldset className="choix-theme">
      <legend className="sr-only">Thème d&apos;affichage</legend>
      {options.map((option) => (
        <label key={option.valeur}>
          <input
            type="radio"
            name="theme"
            value={option.valeur}
            checked={choix === option.valeur}
            onChange={() => setChoix(option.valeur)}
          />
          {option.libelle}
        </label>
      ))}
    </fieldset>
  );
}

function Suppression() {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const formulaire = useFormulaire();
  const [motDePasse, setMotDePasse] = useState("");
  const [certain, setCertain] = useState(false);

  async function soumettre(evenement) {
    evenement.preventDefault();
    const ok = await formulaire.envoyer(
      () => api("/me", { method: "DELETE", body: { password: motDePasse } }),
      null,
    );
    if (ok) {
      setUser(null);
      navigate("/connexion", { replace: true });
    }
  }

  return (
    <form onSubmit={soumettre} noValidate>
      <Champ
        libelle="Mot de passe"
        type="password"
        autoComplete="current-password"
        value={motDePasse}
        onChange={(e) => setMotDePasse(e.target.value)}
        erreur={formulaire.erreurs.current_password}
      />
      <label className="case">
        <input type="checkbox" checked={certain} onChange={(e) => setCertain(e.target.checked)} />
        <span>Je comprends que mon bulletin et toutes mes copies seront effacés, sans retour possible.</span>
      </label>
      <Retours formulaire={formulaire} />
      <button type="submit" className="bouton-2 bouton-danger" disabled={formulaire.envoi || !certain || !motDePasse}>
        Supprimer mon compte
      </button>
    </form>
  );
}

export default function Compte() {
  const meta = useMeta();

  return (
    <>
      <h1>Mon compte</h1>
      <p className="chapeau">
        Vos informations, et tout ce que vous pouvez en faire. Le détail est dans la{" "}
        <Link to="/confidentialite">politique de confidentialité</Link>.
      </p>

      <section className="rubrique">
        <div>
          <h2>Profil</h2>
          <p className="explication">Corriger votre email ou votre nom d&apos;utilisateur.</p>
        </div>
        <Profil />
      </section>

      <section className="rubrique">
        <div>
          <h2>Mot de passe</h2>
          <p className="explication">
            En changer ferme la session sur tous vos autres appareils.
          </p>
        </div>
        <MotDePasse />
      </section>

      <section className="rubrique">
        <div>
          <h2>Apparence</h2>
          <p className="explication">Ce choix reste dans ce navigateur, il n&apos;est pas envoyé au serveur.</p>
        </div>
        <div className="contenu">
          <Apparence />
        </div>
      </section>

      <section className="rubrique">
        <div>
          <h2>Mes données</h2>
          <p className="explication">
            Un fichier JSON avec votre profil, vos leçons terminées, vos copies et leur correction.
          </p>
        </div>
        <div className="contenu">
          {/* Lien direct : le cookie de session accompagne la requête, rien à faire en JavaScript. */}
          <a className="bouton-2" href="/api/me/export" download="revisionna-mes-donnees.json">
            <Icon nom="telecharger" taille={18} /> Télécharger mes données
          </a>
          <p className="aide discret">
            Sans connexion pendant {meta.inactive_account_months} mois, un compte est supprimé
            automatiquement.
          </p>
        </div>
      </section>

      <section className="rubrique danger">
        <div>
          <h2>Supprimer mon compte</h2>
          <p className="explication">Immédiat et définitif : compte, progression, copies, historique.</p>
        </div>
        <Suppression />
      </section>
    </>
  );
}
