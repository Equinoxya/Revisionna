import { Link } from "react-router-dom";

import ACompleter from "../../components/ACompleter.jsx";
import { EDITEUR, HEBERGEUR, JOURNAUX_TECHNIQUES, MISE_A_JOUR } from "../../content/legal.js";
import { useMeta } from "../../lib/meta.js";

const TUTEUR = {
  openai: (
    <>
      Sur ce site, le tuteur utilise <strong>OpenAI</strong>. Quand vous demandez un indice, ces
      éléments sont donc transmis à cette société, aux <strong>États-Unis</strong>, c&apos;est-à-dire
      hors de l&apos;Union européenne. Ce transfert est encadré par le contrat de traitement des
      données conclu avec OpenAI (clauses contractuelles types). Si vous préférez que rien ne
      parte, n&apos;utilisez pas ce bouton : les indices rédigés à l&apos;avance restent disponibles.
    </>
  ),
  ollama: (
    <>
      Sur ce site, le tuteur est un modèle installé sur le serveur lui-même :{" "}
      <strong>rien n&apos;est transmis à un tiers</strong>.
    </>
  ),
  offline: (
    <>
      Sur ce site, aucun modèle d&apos;IA n&apos;est branché pour l&apos;instant : le bouton renvoie
      un conseil générique, et <strong>rien n&apos;est transmis à un tiers</strong>.
    </>
  ),
};

export default function Confidentialite() {
  const meta = useMeta();
  const contact = EDITEUR.contact ? (
    <a href={`mailto:${EDITEUR.contact}`}>{EDITEUR.contact}</a>
  ) : (
    <ACompleter quoi="adresse email de contact" />
  );

  return (
    <article className="document">
      <h1>Politique de confidentialité</h1>
      <p className="mise-a-jour">Mise à jour : {MISE_A_JOUR}</p>

      <p>
        En bref : Revisionna enregistre le strict nécessaire pour tenir votre bulletin. Pas de
        publicité, pas de mesure d&apos;audience, pas de revente, et vous pouvez tout exporter ou
        tout effacer vous-même.
      </p>

      <h2>Qui est responsable de vos données ?</h2>
      <p>
        L&apos;éditeur du site, présenté dans les <Link to="/mentions-legales">mentions légales</Link>.
        Pour toute question : {contact}.
      </p>

      <h2>Ce qui est enregistré, et pourquoi</h2>
      <div className="defilable prose">
        <table>
          <thead>
            <tr>
              <th scope="col">Donnée</th>
              <th scope="col">À quoi elle sert</th>
              <th scope="col">Fondement</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Email, nom d&apos;utilisateur, mot de passe (haché, jamais lisible)</td>
              <td>Créer votre compte et vous reconnaître</td>
              <td>Fourniture du service</td>
            </tr>
            <tr>
              <td>Leçons terminées, notes, code et réponses soumis, retour du correcteur</td>
              <td>Tenir votre bulletin et votre historique</td>
              <td>Fourniture du service</td>
            </tr>
            <tr>
              <td>Date et version des conditions acceptées, date de dernière connexion</td>
              <td>Garder la preuve de votre accord ; supprimer les comptes abandonnés</td>
              <td>Obligation légale, intérêt légitime</td>
            </tr>
            <tr>
              <td>
                Journal d&apos;activité, si l&apos;éditeur l&apos;a activé (connexion, leçon validée,
                copie rendue, indice demandé, avec la date)
              </td>
              <td>Retracer votre activité et faire fonctionner le service</td>
              <td>Intérêt légitime</td>
            </tr>
            <tr>
              <td>
                Compteurs de tentatives de connexion (empreintes chiffrées, sans adresse IP ni
                identifiant en clair) et journaux techniques du serveur (adresse IP, date, page)
              </td>
              <td>Protéger les comptes et repérer les abus</td>
              <td>Intérêt légitime</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p>
        Le site ne demande ni votre nom réel, ni votre téléphone, ni votre adresse, et ne vous
        envoie aucun email.
      </p>

      <h2>Le tuteur IA</h2>
      <p>
        Le bouton « Demander un indice au tuteur IA » fait appel à un programme d&apos;intelligence
        artificielle, pas à une personne. Il reçoit l&apos;énoncé de l&apos;exercice, votre code et
        le résultat des tests ; jamais votre email ni votre nom d&apos;utilisateur. Ses réponses
        peuvent être fausses.
      </p>
      <p>{TUTEUR[meta.ai_provider] ?? TUTEUR.offline}</p>

      <h2>Qui y a accès ?</h2>
      <ul>
        <li>L&apos;éditeur du site, pour l&apos;administrer.</li>
        <li>
          L&apos;hébergeur (<ACompleter valeur={HEBERGEUR.nom} quoi="nom de l'hébergeur" />, serveurs
          situés en <ACompleter valeur={HEBERGEUR.pays} quoi="pays d'hébergement" />), qui stocke les
          données pour le compte de l&apos;éditeur.
        </li>
        {meta.ai_external && <li>OpenAI, uniquement pour les demandes d&apos;indice (voir plus haut).</li>}
      </ul>
      <p>Personne d&apos;autre. Vos données ne sont ni vendues, ni louées, ni échangées.</p>

      <h2>Combien de temps ?</h2>
      <ul>
        <li>
          <strong>Votre compte et votre travail</strong> : jusqu&apos;à ce que vous supprimiez le
          compte, ou {meta.inactive_account_months} mois après votre dernière connexion.
        </li>
        <li>
          <strong>Journal d&apos;activité</strong> : {meta.activity_retention_days} jours, puis
          effacement automatique.
        </li>
        <li>
          <strong>Compteurs de tentatives de connexion</strong> : 24 heures au plus.
        </li>
        <li>
          <strong>Journaux techniques du serveur</strong> :{" "}
          <ACompleter valeur={JOURNAUX_TECHNIQUES} quoi="durée de conservation des journaux (6 à 12 mois recommandés)" />.
        </li>
      </ul>

      <h2>Cookies et stockage dans votre navigateur</h2>
      <p>
        Trois éléments seulement, tous indispensables au fonctionnement : c&apos;est pourquoi
        aucun bandeau ne vous demande votre accord.
      </p>
      <div className="defilable prose">
        <table>
          <thead>
            <tr>
              <th scope="col">Nom</th>
              <th scope="col">Rôle</th>
              <th scope="col">Durée</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <code>revisionna_session</code> (cookie)
              </td>
              <td>Vous garder connecté. Illisible par les scripts de la page.</td>
              <td>Jusqu&apos;à la fermeture du navigateur, {meta.session_hours} h au plus</td>
            </tr>
            <tr>
              <td>
                <code>revisionna_csrf</code> (cookie)
              </td>
              <td>Empêcher un autre site d&apos;agir à votre place</td>
              <td>Identique</td>
            </tr>
            <tr>
              <td>
                <code>revisionna.theme</code> (stockage local)
              </td>
              <td>Retenir votre choix entre cahier et tableau noir</td>
              <td>Jusqu&apos;à ce que vous l&apos;effaciez</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p>Aucun cookie publicitaire, aucun traceur, aucune ressource chargée depuis un autre site.</p>

      <h2>Vos droits</h2>
      <ul>
        <li>
          <strong>Accéder à vos données et les récupérer</strong> : bouton « Télécharger mes
          données » dans <Link to="/compte">Mon compte</Link>.
        </li>
        <li>
          <strong>Les corriger</strong> : rubrique « Profil » de la même page.
        </li>
        <li>
          <strong>Les effacer</strong> : « Supprimer mon compte », effet immédiat et définitif.
        </li>
        <li>
          <strong>Vous opposer à un traitement, le limiter, ou poser une question</strong> : {contact}.
          Une réponse vous est due dans un délai d&apos;un mois.
        </li>
      </ul>
      <p>
        Si la réponse ne vous convient pas, vous pouvez saisir la CNIL (
        <a href="https://www.cnil.fr/fr/plaintes" rel="noopener noreferrer">
          cnil.fr/fr/plaintes
        </a>
        ).
      </p>

      <h2>Sécurité</h2>
      <p>
        Les mots de passe sont stockés sous forme hachée (scrypt), la connexion se bloque
        temporairement après plusieurs échecs, la session tient dans un cookie inaccessible aux
        scripts, et le code que vous soumettez s&apos;exécute dans un environnement isolé, sans
        réseau ni accès aux données du site.
      </p>

      <h2>Âge</h2>
      <p>
        Le site s&apos;adresse aux personnes de 15 ans et plus. En dessous, l&apos;inscription
        demande l&apos;accord d&apos;un parent.
      </p>
    </article>
  );
}
