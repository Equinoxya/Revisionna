import { Link } from "react-router-dom";

import ACompleter from "../../components/ACompleter.jsx";
import { EDITEUR, HEBERGEUR, MISE_A_JOUR } from "../../content/legal.js";

export default function MentionsLegales() {
  const contact = EDITEUR.contact ? (
    <a href={`mailto:${EDITEUR.contact}`}>{EDITEUR.contact}</a>
  ) : (
    <ACompleter quoi="adresse email de contact" />
  );

  return (
    <article className="document">
      <h1>Mentions légales</h1>
      <p className="mise-a-jour">Mise à jour : {MISE_A_JOUR}</p>

      <h2>Éditeur du site</h2>
      {EDITEUR.nom ? (
        <p>
          {EDITEUR.nom}
          <br />
          <ACompleter valeur={EDITEUR.adresse} quoi="adresse de l'éditeur" />
        </p>
      ) : (
        <p>
          Revisionna est édité à titre non professionnel par une personne physique. Comme la loi
          pour la confiance dans l&apos;économie numérique le permet, son nom et son adresse ont
          été communiqués à l&apos;hébergeur ci-dessous plutôt que publiés ici.
        </p>
      )}
      <p>Contact : {contact}</p>
      <p>
        Directeur de la publication : {EDITEUR.nom || "l'éditeur du site"}.
      </p>

      <h2>Hébergeur</h2>
      <p>
        <ACompleter valeur={HEBERGEUR.nom} quoi="nom de l'hébergeur" />
        <br />
        <ACompleter valeur={HEBERGEUR.adresse} quoi="adresse de l'hébergeur" />
        <br />
        Téléphone : <ACompleter valeur={HEBERGEUR.telephone} quoi="téléphone de l'hébergeur" />
      </p>

      <h2>Propriété intellectuelle</h2>
      <p>
        Les leçons, énoncés et corrigés ont été rédigés pour ce site. Vous pouvez les utiliser pour
        votre apprentissage personnel ; toute republication demande l&apos;accord de l&apos;éditeur.
      </p>
      <p>Le code et les réponses que vous soumettez restent les vôtres.</p>

      <h2>Données personnelles</h2>
      <p>
        Ce que le site enregistre, pourquoi, combien de temps, et comment exercer vos droits : tout
        est dans la <Link to="/confidentialite">politique de confidentialité</Link>.
      </p>

      <h2>Signaler un problème</h2>
      <p>
        Une erreur dans un cours, un contenu qui ne devrait pas être là, une faille de sécurité :
        écrivez à {contact}.
      </p>
    </article>
  );
}
