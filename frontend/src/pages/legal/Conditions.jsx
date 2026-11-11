import { Link } from "react-router-dom";

import { MISE_A_JOUR } from "../../content/legal.js";
import { useMeta } from "../../lib/meta.js";

export default function Conditions() {
  const meta = useMeta();

  return (
    <article className="document">
      <h1>Conditions d&apos;utilisation</h1>
      <p className="mise-a-jour">
        Mise à jour : {MISE_A_JOUR}
        {meta.terms_version && <> · version {meta.terms_version}</>}
      </p>

      <h2>1. Ce qu&apos;est Revisionna</h2>
      <p>
        Un site d&apos;entraînement : des leçons à lire, des questions pour vérifier, des travaux
        pratiques corrigés automatiquement. C&apos;est un projet pédagogique gratuit, tenu par un
        particulier, sans lien avec un organisme de formation et sans valeur de diplôme.
      </p>

      <h2>2. Votre compte</h2>
      <ul>
        <li>Un compte par personne, à partir de 15 ans (ou avec l&apos;accord d&apos;un parent).</li>
        <li>Choisissez un mot de passe que vous n&apos;utilisez nulle part ailleurs, et gardez-le pour vous.</li>
        <li>Vous pouvez supprimer votre compte à tout moment depuis « Mon compte ».</li>
      </ul>

      <h2>3. Ce qui est attendu de vous</h2>
      <p>
        Le site exécute le code que vous lui envoyez. Cette possibilité existe pour apprendre, pas
        pour autre chose. Il est donc interdit :
      </p>
      <ul>
        <li>de chercher à sortir de l&apos;environnement d&apos;exécution ou à atteindre d&apos;autres machines ;</li>
        <li>d&apos;utiliser le site pour du calcul sans rapport avec les exercices ;</li>
        <li>de tenter d&apos;accéder au compte ou aux copies de quelqu&apos;un d&apos;autre ;</li>
        <li>de saturer le service, par exemple avec des envois automatisés.</li>
      </ul>
      <p>
        Vous avez trouvé une faille ? Signalez-la à l&apos;éditeur (voir les{" "}
        <Link to="/mentions-legales">mentions légales</Link>) plutôt que de l&apos;exploiter : merci
        d&apos;avance.
      </p>

      <h2>4. Le correcteur et le tuteur IA</h2>
      <p>
        Les notes sont calculées par des tests automatiques. Elles servent à vous situer, rien de
        plus. Le tuteur IA est un programme : ses indices peuvent être imprécis ou faux, et ne
        remplacent ni le cours ni un formateur.
      </p>

      <h2>5. Les contenus</h2>
      <p>
        Les leçons et les énoncés appartiennent à l&apos;éditeur ; vous pouvez les utiliser pour
        apprendre, pas les republier. Ce que vous écrivez reste à vous : le site le conserve
        uniquement pour afficher votre historique et votre bulletin.
      </p>

      <h2>6. Disponibilité</h2>
      <p>
        Le site est fourni tel quel, sans garantie de disponibilité ni de conservation. Il peut
        être interrompu ou arrêté. Exportez vos données si vous y tenez.
      </p>

      <h2>7. En cas d&apos;abus</h2>
      <p>
        L&apos;éditeur peut suspendre ou supprimer un compte qui ne respecte pas ces règles, en
        particulier celles du point 3.
      </p>

      <h2>8. Vos données</h2>
      <p>
        Elles sont traitées comme l&apos;explique la{" "}
        <Link to="/confidentialite">politique de confidentialité</Link>.
      </p>

      <h2>9. Évolution et droit applicable</h2>
      <p>
        Les conditions en vigueur sont celles de cette page ; la version acceptée à votre
        inscription est conservée avec votre compte. Elles relèvent du droit français.
      </p>
    </article>
  );
}
