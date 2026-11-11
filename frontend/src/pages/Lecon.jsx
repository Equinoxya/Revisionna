import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import Markdown from "../components/Markdown.jsx";
import Quiz from "../components/Quiz.jsx";
import { api } from "../lib/api.js";

export default function Lecon() {
  const { coursSlug, leconSlug } = useParams();
  const navigate = useNavigate();

  const [donnees, setDonnees] = useState(null);
  const [erreur, setErreur] = useState(null);
  const [reponses, setReponses] = useState({});
  const [correction, setCorrection] = useState(null);
  const [envoi, setEnvoi] = useState(false);

  useEffect(() => {
    let annule = false;
    setDonnees(null);
    setReponses({});
    setCorrection(null);
    api(`/courses/${coursSlug}/lessons/${leconSlug}`)
      .then((data) => {
        if (!annule) setDonnees(data);
      })
      .catch((exception) => {
        if (!annule) setErreur(exception.message);
      });
    return () => {
      annule = true;
    };
  }, [coursSlug, leconSlug]);

  async function valider() {
    setEnvoi(true);
    try {
      const data = await api(`/courses/${coursSlug}/lessons/${leconSlug}/complete`, {
        method: "POST",
        body: { answers: reponses },
      });
      setCorrection(data);
    } catch (exception) {
      setErreur(exception.message);
    } finally {
      setEnvoi(false);
    }
  }

  if (erreur) return <p className="alerte">{erreur}</p>;
  if (!donnees) return <p className="etat">Chargement...</p>;

  const { lesson, course, prev, next, done } = donnees;
  const quizzes = lesson.blocks.filter((bloc) => bloc.type === "quiz");
  const resultatsParId = Object.fromEntries((correction?.results || []).map((r) => [r.id, r]));

  return (
    <article className="lecon">
      <Link to={`/cours/${course.slug}`} className="retour-lien">
        &larr; {course.title}
      </Link>

      <h1>{lesson.title}</h1>
      <p className="sous-titre">
        {lesson.duration_min} min {done && !correction ? "- deja validee" : ""}
      </p>

      {lesson.blocks.map((bloc, index) => {
        const cle = `${bloc.type}-${bloc.id ?? index}`;

        if (bloc.type === "text") return <Markdown key={cle}>{bloc.md}</Markdown>;

        if (bloc.type === "code") {
          return (
            <pre key={cle} className="bloc-code">
              <code>{bloc.code}</code>
            </pre>
          );
        }

        if (bloc.type === "callout") {
          return (
            <aside key={cle} className={`encart ${bloc.tone || "info"}`}>
              <Markdown>{bloc.md}</Markdown>
            </aside>
          );
        }

        if (bloc.type === "quiz") {
          return (
            <Quiz
              key={cle}
              nom={`quiz-${bloc.id}`}
              question={bloc.question}
              choix={bloc.choices}
              valeur={reponses[bloc.id]}
              onChange={(valeur) => setReponses({ ...reponses, [bloc.id]: valeur })}
              resultat={resultatsParId[bloc.id]}
            />
          );
        }
        return null;
      })}

      <div className="barre-actions">
        {!correction ? (
          <button type="button" className="bouton" onClick={valider} disabled={envoi}>
            {envoi
              ? "Validation..."
              : quizzes.length
                ? "Valider mes reponses"
                : "Marquer comme terminee"}
          </button>
        ) : (
          <p className="score">
            Score du quiz : <strong>{Math.round(correction.score * 100)}%</strong> - lecon validee.
          </p>
        )}

        <div className="navigation">
          {prev && (
            <button
              type="button"
              className="bouton-secondaire"
              onClick={() => navigate(`/cours/${course.slug}/lecons/${prev}`)}
            >
              &larr; Precedente
            </button>
          )}
          {next && (
            <button
              type="button"
              className="bouton-secondaire"
              onClick={() => navigate(`/cours/${course.slug}/lecons/${next}`)}
            >
              Suivante &rarr;
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
