import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import Markdown from "../components/Markdown.jsx";
import Quiz from "../components/Quiz.jsx";
import { api } from "../lib/api.js";

export default function Exercice() {
  const { coursSlug, exerciceSlug } = useParams();

  const [donnees, setDonnees] = useState(null);
  const [erreur, setErreur] = useState(null);
  const [code, setCode] = useState("");
  const [reponses, setReponses] = useState({});
  const [resultat, setResultat] = useState(null);
  const [envoi, setEnvoi] = useState(false);
  const [indicesVisibles, setIndicesVisibles] = useState(0);
  const [indiceIA, setIndiceIA] = useState(null);
  const [chargementIA, setChargementIA] = useState(false);

  useEffect(() => {
    let annule = false;
    setDonnees(null);
    setResultat(null);
    setReponses({});
    setIndicesVisibles(0);
    setIndiceIA(null);
    api(`/courses/${coursSlug}/exercises/${exerciceSlug}`)
      .then((data) => {
        if (annule) return;
        setDonnees(data);
        setCode(data.exercise.starter_code || "");
      })
      .catch((exception) => {
        if (!annule) setErreur(exception.message);
      });
    return () => {
      annule = true;
    };
  }, [coursSlug, exerciceSlug]);

  const exercice = donnees?.exercise;

  const resultatsParId = useMemo(
    () => Object.fromEntries((resultat?.results || []).map((r) => [r.id, r])),
    [resultat],
  );

  async function soumettre() {
    setEnvoi(true);
    setIndiceIA(null);
    try {
      const corps = exercice.kind === "quiz" ? { answers: reponses } : { code };
      setResultat(await api(`/exercises/${exercice.id}/submit`, { method: "POST", body: corps }));
    } catch (exception) {
      setErreur(exception.message);
    } finally {
      setEnvoi(false);
    }
  }

  async function demanderIndiceIA() {
    setChargementIA(true);
    try {
      setIndiceIA(
        await api(`/exercises/${exercice.id}/hint`, {
          method: "POST",
          body: { code, output: resultat?.output || "" },
        }),
      );
    } catch (exception) {
      setIndiceIA({ provider: "erreur", answer: exception.message });
    } finally {
      setChargementIA(false);
    }
  }

  /** Tabulation = indentation, au lieu de sortir du champ. */
  function gererTabulation(evenement) {
    if (evenement.key !== "Tab") return;
    evenement.preventDefault();
    const { selectionStart, selectionEnd, value } = evenement.target;
    const nouveau = `${value.slice(0, selectionStart)}    ${value.slice(selectionEnd)}`;
    setCode(nouveau);
    requestAnimationFrame(() => {
      evenement.target.selectionStart = selectionStart + 4;
      evenement.target.selectionEnd = selectionStart + 4;
    });
  }

  if (erreur) return <p className="alerte">{erreur}</p>;
  if (!donnees) return <p className="etat">Chargement...</p>;

  const indices = exercice.hints || [];

  return (
    <article className="exercice">
      <Link to={`/cours/${donnees.course.slug}`} className="retour-lien">
        &larr; {donnees.course.title}
      </Link>

      <header className="entete-exercice">
        <h1>{exercice.title}</h1>
        <span className="niveau">{exercice.difficulty}</span>
      </header>

      <div className="atelier">
        <section className="enonce">
          <h2>Enonce</h2>
          <Markdown>{exercice.statement}</Markdown>

          {exercice.kind === "sql" && exercice.spec.schema && (
            <details className="schema">
              <summary>Schema de la base</summary>
              <pre className="bloc-code">
                <code>{exercice.spec.schema.trim()}</code>
              </pre>
            </details>
          )}

          {indices.length > 0 && (
            <div className="indices">
              <h3>Indices</h3>
              <ol>
                {indices.slice(0, indicesVisibles).map((indice) => (
                  <li key={indice}>{indice}</li>
                ))}
              </ol>
              {indicesVisibles < indices.length && (
                <button
                  type="button"
                  className="bouton-secondaire"
                  onClick={() => setIndicesVisibles(indicesVisibles + 1)}
                >
                  Afficher un indice ({indicesVisibles}/{indices.length})
                </button>
              )}
            </div>
          )}
        </section>

        <section className="editeur">
          {exercice.kind === "quiz" ? (
            <>
              <h2>Questions</h2>
              {exercice.spec.questions.map((question) => (
                <Quiz
                  key={question.id}
                  nom={`q-${question.id}`}
                  question={question.question}
                  choix={question.choices}
                  valeur={reponses[question.id]}
                  onChange={(valeur) => setReponses({ ...reponses, [question.id]: valeur })}
                  resultat={resultatsParId[question.id]}
                />
              ))}
            </>
          ) : (
            <>
              <h2>{exercice.kind === "sql" ? "Votre requete SQL" : "Votre code Python"}</h2>
              <textarea
                className="champ-code"
                spellCheck="false"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                onKeyDown={gererTabulation}
                rows={18}
              />
            </>
          )}

          <div className="barre-actions">
            <button type="button" className="bouton" onClick={soumettre} disabled={envoi}>
              {envoi ? "Correction..." : "Lancer la correction"}
            </button>

            {exercice.kind !== "quiz" && (
              <button
                type="button"
                className="bouton-secondaire"
                onClick={() => setCode(exercice.starter_code || "")}
              >
                Reinitialiser
              </button>
            )}

            <button
              type="button"
              className="bouton-secondaire"
              onClick={demanderIndiceIA}
              disabled={chargementIA}
            >
              {chargementIA ? "..." : "Demander un indice a l'IA"}
            </button>
          </div>

          {indiceIA && (
            <aside className="encart info">
              <p>
                <strong>Tuteur IA</strong> <small>({indiceIA.provider})</small>
              </p>
              <p>{indiceIA.answer}</p>
            </aside>
          )}

          {resultat && (
            <div className={resultat.passed ? "resultat ok" : "resultat ko"}>
              <p className="resume">
                {resultat.passed ? "Tous les tests passent." : "Il reste des erreurs."}{" "}
                Score : {Math.round(resultat.score * 100)}%
              </p>
              {resultat.output && <pre className="sortie">{resultat.output}</pre>}
              {resultat.solution && (
                <details className="solution">
                  <summary>Voir une solution de reference</summary>
                  <pre className="bloc-code">
                    <code>{resultat.solution}</code>
                  </pre>
                </details>
              )}
            </div>
          )}
        </section>
      </div>
    </article>
  );
}
