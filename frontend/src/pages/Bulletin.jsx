import { Link } from "react-router-dom";

import Monogramme from "../components/Monogramme.jsx";
import Note from "../components/Note.jsx";
import { useAuth } from "../lib/AuthContext.jsx";
import { appreciation, dateDuJour, dateRelative, surVingt } from "../lib/format.js";
import { useApi } from "../lib/useApi.js";

export default function Bulletin() {
  const { user } = useAuth();
  const { donnees, erreur } = useApi("/me/dashboard");

  if (erreur) return <p className="message erreur">{erreur}</p>;
  if (!donnees) return <p className="etat">Le bulletin arrive…</p>;

  const { totals, courses, recent_submissions: copies } = donnees;
  const vierge = totals.lessons_done === 0 && totals.submissions === 0;

  return (
    <>
      <div className="tete-bulletin">
        <div>
          <span className="date-du-jour">{dateDuJour()}</span>
          <h1>Bulletin de {user.username}</h1>
          <p className="chapeau">
            {vierge ? (
              <>
                Rien de noté pour l&apos;instant. Ouvrez le <Link to="/cours">sommaire</Link> et
                choisissez une première leçon.
              </>
            ) : (
              <>
                {totals.lessons_done} leçon{totals.lessons_done > 1 ? "s" : ""} sur {totals.lessons_total},{" "}
                {totals.exercises_passed} TP réussi{totals.exercises_passed > 1 ? "s" : ""} sur{" "}
                {totals.exercises_total}.
              </>
            )}
          </p>
        </div>

        {totals.average !== null && (
          <div className="moyenne-generale">
            <span className="intitule">Moyenne générale</span>
            <Note score={totals.average} grande libelle="Moyenne générale" />
          </div>
        )}
      </div>

      <table className="bulletin">
        <caption className="sr-only">Avancement et moyenne par matière</caption>
        <thead>
          <tr>
            <th scope="col">Matière</th>
            <th scope="col">Leçons</th>
            <th scope="col">TP</th>
            <th scope="col">Moyenne</th>
            <th scope="col">Appréciation</th>
          </tr>
        </thead>
        <tbody>
          {courses.map((cours) => (
            <tr key={cours.slug}>
              <td className="matiere">
                <Link to={`/cours/${cours.slug}`}>
                  <Monogramme cours={cours} />
                  <span className="intitule-cours">{cours.title}</span>
                </Link>
              </td>
              <td className="nombre" data-titre="Leçons">
                {cours.lessons_done}/{cours.lessons_total}
              </td>
              <td className="nombre" data-titre="TP">
                {cours.exercises_passed}/{cours.exercises_total}
              </td>
              <td className="moyenne" data-titre="Moyenne">
                {cours.average === null ? (
                  <span className="discret" aria-label="pas encore de note">
                    —
                  </span>
                ) : (
                  <>
                    {surVingt(cours.average)}
                    <small>/20</small>
                  </>
                )}
              </td>
              <td className="appreciation">{appreciation(cours)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {copies.length > 0 && (
        <>
          <h2>Dernières copies rendues</h2>
          <ul className="copies">
            {copies.map((copie) => (
              <li key={copie.id}>
                <Link to={`/cours/${copie.course_slug}/exercices/${copie.exercise_slug}`}>
                  {copie.exercise_title}
                </Link>
                <span className="pointilles" aria-hidden="true" />
                <span className={`resultat ${copie.passed ? "marque-ok" : "marque-ko"}`}>
                  {surVingt(copie.score)}/20
                </span>
                <time dateTime={copie.created_at}>{dateRelative(copie.created_at)}</time>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
}
