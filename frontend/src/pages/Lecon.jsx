import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import Icon from "../components/Icon.jsx";
import Markdown from "../components/Markdown.jsx";
import Note from "../components/Note.jsx";
import Quiz from "../components/Quiz.jsx";
import { api } from "../lib/api.js";
import { mention, surVingt } from "../lib/format.js";
import { useApi } from "../lib/useApi.js";

export default function Lecon() {
  const { coursSlug, leconSlug } = useParams();
  const chemin = `/courses/${coursSlug}/lessons/${leconSlug}`;
  const { donnees, erreur } = useApi(chemin);

  if (erreur) return <p className="message erreur">{erreur}</p>;
  if (!donnees) return <p className="etat">Ouverture de la leçon…</p>;
  // `key` : en changeant de leçon, on repart d'une feuille blanche (réponses, correction).
  return <Feuille key={chemin} chemin={chemin} donnees={donnees} />;
}

function Bloc({ bloc, numero, reponses, setReponses, resultat }) {
  switch (bloc.type) {
    case "text":
      return <Markdown>{bloc.md}</Markdown>;
    case "code":
      return (
        <div className="listing prose">
          {bloc.lang && <span className="langage">{bloc.lang}</span>}
          <pre>
            <code>{bloc.code}</code>
          </pre>
        </div>
      );
    case "callout":
      return (
        <aside className={bloc.tone === "warn" ? "annotation attention" : "annotation"}>
          <span className="titre-annotation">{bloc.tone === "warn" ? "Attention" : "À retenir"}</span>
          <Markdown>{bloc.md}</Markdown>
        </aside>
      );
    case "quiz":
      return (
        <Quiz
          numero={numero}
          nom={`question-${bloc.id}`}
          question={bloc.question}
          choix={bloc.choices}
          valeur={reponses[bloc.id]}
          onChange={(valeur) => setReponses({ ...reponses, [bloc.id]: valeur })}
          resultat={resultat}
        />
      );
    default:
      return null;
  }
}

function Feuille({ chemin, donnees }) {
  const { lesson, course, prev, next, done, quiz_score: ancienScore } = donnees;
  const [reponses, setReponses] = useState({});
  const [correction, setCorrection] = useState(null);
  const [envoi, setEnvoi] = useState(false);
  const [erreur, setErreur] = useState(null);

  const questions = lesson.blocks.filter((bloc) => bloc.type === "quiz");
  const resultats = Object.fromEntries((correction?.results ?? []).map((r) => [r.id, r]));
  const repondues = questions.filter((q) => reponses[q.id] !== undefined).length;

  async function valider() {
    setEnvoi(true);
    setErreur(null);
    try {
      setCorrection(await api(`${chemin}/complete`, { method: "POST", body: { answers: reponses } }));
    } catch (exception) {
      setErreur(exception.message);
    } finally {
      setEnvoi(false);
    }
  }

  function recommencer() {
    setReponses({});
    setCorrection(null);
  }

  let numero = 0;

  return (
    <article>
      <Link to={`/cours/${course.slug}`} className="fil">
        <Icon nom="gauche" taille={16} /> {course.title}
      </Link>

      <h1>{lesson.title}</h1>
      <p className="meta-lecon">
        <span>Lecture : {lesson.duration_min} min</span>
        {questions.length > 0 && (
          <span>
            {questions.length} question{questions.length > 1 ? "s" : ""} en fin de leçon
          </span>
        )}
        {done && !correction && (
          <span className="marque-ok">
            Déjà validée{ancienScore !== null && questions.length > 0 ? ` (${surVingt(ancienScore)}/20)` : ""}
          </span>
        )}
      </p>

      {lesson.blocks.map((bloc, index) => {
        if (bloc.type === "quiz") numero += 1;
        return (
          <Bloc
            key={`${bloc.type}-${bloc.id ?? index}`}
            bloc={bloc}
            numero={numero}
            reponses={reponses}
            setReponses={setReponses}
            resultat={resultats[bloc.id]}
          />
        );
      })}

      <div className="fin-de-lecon" aria-live="polite">
        {erreur && <p className="message erreur">{erreur}</p>}

        {correction ? (
          <div className="bilan">
            {questions.length > 0 && <Note score={correction.score} />}
            <p>
              <strong>Leçon validée.</strong>{" "}
              {questions.length > 0 && <span className="cursive discret">{mention(correction.score)}</span>}
            </p>
            {questions.length > 0 && correction.score < 1 && (
              <button type="button" className="lien-bouton" onClick={recommencer}>
                Refaire les questions
              </button>
            )}
          </div>
        ) : (
          <div className="actions">
            <button type="button" className="bouton" onClick={valider} disabled={envoi}>
              {envoi ? "Correction…" : questions.length > 0 ? "Faire corriger mes réponses" : "J'ai lu cette leçon"}
            </button>
            {questions.length > 0 && (
              <span className="discret">
                {repondues}/{questions.length} réponse{repondues > 1 ? "s" : ""}
              </span>
            )}
          </div>
        )}
      </div>

      <nav className="pagination" aria-label="Leçons du chapitre">
        {prev && (
          <Link to={`/cours/${course.slug}/lecons/${prev}`}>
            <Icon nom="gauche" taille={16} /> Leçon précédente
          </Link>
        )}
        {next ? (
          <Link to={`/cours/${course.slug}/lecons/${next}`} className="suivante">
            Leçon suivante <Icon nom="droite" taille={16} />
          </Link>
        ) : (
          <Link to={`/cours/${course.slug}`} className="suivante">
            Passer aux TP <Icon nom="droite" taille={16} />
          </Link>
        )}
      </nav>
    </article>
  );
}
