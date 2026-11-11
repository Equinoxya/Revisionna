import { useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import Difficulte from "../components/Difficulte.jsx";
import Icon from "../components/Icon.jsx";
import Markdown from "../components/Markdown.jsx";
import Note from "../components/Note.jsx";
import Quiz from "../components/Quiz.jsx";
import { api } from "../lib/api.js";
import { mention } from "../lib/format.js";
import { useMeta } from "../lib/meta.js";
import { useApi } from "../lib/useApi.js";

const GENRES = { python: "Python", sql: "SQL", quiz: "QCM" };

// Dire clairement à qui parle l'élève, et où part son code, avant qu'il ne l'envoie.
const TRANSPARENCE_IA = {
  openai:
    "L'indice est rédigé par une IA. Votre code et l'énoncé sont envoyés à OpenAI (États-Unis) ; ni votre email ni votre nom d'utilisateur ne le sont.",
  ollama:
    "L'indice est rédigé par une IA hébergée sur ce serveur : votre code ne quitte pas le site.",
  offline:
    "Aucun modèle d'IA n'est branché sur ce serveur : vous recevrez un conseil générique.",
};

export default function Exercice() {
  const { coursSlug, exerciceSlug } = useParams();
  const chemin = `/courses/${coursSlug}/exercises/${exerciceSlug}`;
  const { donnees, erreur } = useApi(chemin);

  if (erreur) return <p className="message erreur">{erreur}</p>;
  if (!donnees) return <p className="etat">Distribution du sujet…</p>;
  return <Copie key={chemin} exercice={donnees.exercise} cours={donnees.course} />;
}

/** 11.166666666666666 -> « 11.1667 » : quatre décimales suffisent pour comparer. */
function cellule(valeur) {
  if (valeur === null) return <span className="discret">NULL</span>;
  if (typeof valeur === "number" && !Number.isInteger(valeur)) return String(Number(valeur.toFixed(4)));
  return String(valeur);
}

function Tableau({ colonnes, lignes }) {
  if (!lignes?.length) return <p className="discret">Aucune ligne.</p>;
  return (
    <div className="defilable">
      <table className="tableau chiffres">
        {colonnes?.length > 0 && (
          <thead>
            <tr>
              {colonnes.map((colonne, index) => (
                <th key={index} scope="col">
                  {colonne}
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {lignes.map((ligne, i) => (
            <tr key={i}>
              {ligne.map((valeur, j) => (
                <td key={j}>{cellule(valeur)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Copie({ exercice, cours }) {
  const meta = useMeta();
  const [code, setCode] = useState(exercice.starter_code || "");
  const [reponses, setReponses] = useState({});
  const [resultat, setResultat] = useState(null);
  const [envoi, setEnvoi] = useState(false);
  const [erreur, setErreur] = useState(null);
  const [indicesVisibles, setIndicesVisibles] = useState(0);
  const [indiceIA, setIndiceIA] = useState(null);
  const [chargementIA, setChargementIA] = useState(false);
  const sortieTab = useRef(false);

  const estQuiz = exercice.kind === "quiz";
  const indices = exercice.hints || [];
  const parQuestion = Object.fromEntries((resultat?.results ?? []).map((r) => [r.id, r]));

  async function rendre() {
    setEnvoi(true);
    setErreur(null);
    setIndiceIA(null);
    try {
      const corps = estQuiz ? { answers: reponses } : { code };
      setResultat(await api(`/exercises/${exercice.id}/submit`, { method: "POST", body: corps }));
    } catch (exception) {
      setErreur(exception.message);
    } finally {
      setEnvoi(false);
    }
  }

  async function demanderIndice() {
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

  /** Tab indente ; Échap puis Tab rend la main au clavier (pas de piège à focus). */
  function clavier(evenement) {
    if (evenement.key === "Escape") {
      sortieTab.current = true;
      return;
    }
    if (evenement.key !== "Tab" || evenement.shiftKey || sortieTab.current) {
      sortieTab.current = false;
      return;
    }
    evenement.preventDefault();
    const zone = evenement.target;
    const { selectionStart, selectionEnd, value } = zone;
    setCode(`${value.slice(0, selectionStart)}    ${value.slice(selectionEnd)}`);
    requestAnimationFrame(() => {
      zone.selectionStart = selectionStart + 4;
      zone.selectionEnd = selectionStart + 4;
    });
  }

  return (
    <article>
      <Link to={`/cours/${cours.slug}`} className="fil">
        <Icon nom="gauche" taille={16} /> {cours.title}
      </Link>

      <div className="tete-copie">
        <div>
          <h1>{exercice.title}</h1>
          <div className="infos">
            <span className="etiquette">{GENRES[exercice.kind] ?? exercice.kind}</span>
            <Difficulte valeur={exercice.difficulty} />
          </div>
        </div>
        {resultat && <Note score={resultat.score} grande />}
      </div>

      <div className="atelier">
        <section>
          <h2>Énoncé</h2>
          <Markdown>{exercice.statement}</Markdown>

          {exercice.kind === "sql" && exercice.spec.schema && (
            <details className="repli">
              <summary>Voir les tables et leurs données</summary>
              <div className="listing">
                <span className="langage">sql</span>
                <pre>
                  <code>{exercice.spec.schema.trim()}</code>
                </pre>
              </div>
            </details>
          )}

          {indices.length > 0 && (
            <div className="indices">
              <h2 className="suite">Indices</h2>
              {indicesVisibles > 0 && (
                <ol>
                  {indices.slice(0, indicesVisibles).map((indice) => (
                    <li key={indice}>
                      <Markdown>{indice}</Markdown>
                    </li>
                  ))}
                </ol>
              )}
              {indicesVisibles < indices.length ? (
                <button
                  type="button"
                  className="bouton-2"
                  onClick={() => setIndicesVisibles(indicesVisibles + 1)}
                >
                  {indicesVisibles === 0 ? "Un indice" : "Un autre indice"} ({indicesVisibles}/{indices.length})
                </button>
              ) : (
                <p className="discret">Tous les indices sont affichés.</p>
              )}
            </div>
          )}
        </section>

        <section>
          {estQuiz ? (
            <>
              <h2>Questions</h2>
              {exercice.spec.questions.map((question, index) => (
                <Quiz
                  key={question.id}
                  numero={index + 1}
                  nom={`question-${question.id}`}
                  question={question.question}
                  choix={question.choices}
                  valeur={reponses[question.id]}
                  onChange={(valeur) => setReponses({ ...reponses, [question.id]: valeur })}
                  resultat={parQuestion[question.id]}
                />
              ))}
            </>
          ) : (
            <>
              <h2 id="titre-copie">{exercice.kind === "sql" ? "Votre requête" : "Votre code"}</h2>
              <textarea
                className="copie"
                aria-labelledby="titre-copie"
                aria-describedby="aide-copie"
                spellCheck="false"
                autoCapitalize="off"
                autoCorrect="off"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                onKeyDown={clavier}
              />
              <p className="aide discret" id="aide-copie">
                Tab indente. Pour quitter la zone au clavier : Échap, puis Tab.
              </p>
            </>
          )}

          <div className="actions">
            {estQuiz && resultat ? (
              <button
                type="button"
                className="bouton-2"
                onClick={() => {
                  setResultat(null);
                  setReponses({});
                }}
              >
                Recommencer
              </button>
            ) : (
              <button type="button" className="bouton" onClick={rendre} disabled={envoi}>
                {envoi ? "Correction…" : "Rendre la copie"}
              </button>
            )}
            {!estQuiz && (
              <>
                <button
                  type="button"
                  className="lien-bouton"
                  onClick={() => setCode(exercice.starter_code || "")}
                >
                  Réinitialiser
                </button>
                <button type="button" className="bouton-2" onClick={demanderIndice} disabled={chargementIA}>
                  {chargementIA ? "Le tuteur réfléchit…" : "Demander un indice au tuteur IA"}
                </button>
              </>
            )}
          </div>
          {!estQuiz && (
            <p className="transparence">{TRANSPARENCE_IA[meta.ai_provider] ?? TRANSPARENCE_IA.offline}</p>
          )}

          <div aria-live="polite">
            {erreur && <p className="message erreur">{erreur}</p>}

            {indiceIA && (
              <aside className="annotation">
                <span className="titre-annotation">Le tuteur IA</span>
                <p>{indiceIA.answer}</p>
                <p className="discret">
                  <small>Réponse générée automatiquement : elle peut se tromper.</small>
                </p>
              </aside>
            )}

            {resultat && (
              <>
                <h2 className="suite">Correction</h2>
                <p className={`verdict-copie ${resultat.passed ? "marque-ok" : "marque-ko"}`}>
                  {resultat.passed ? "Copie validée." : "Pas encore."}{" "}
                  <span className="cursive discret">{mention(resultat.score)}</span>
                </p>

                {exercice.kind === "python" && resultat.results.length > 0 && (
                  <ul className="rapport">
                    {resultat.results.map((test) => (
                      <li key={test.name}>
                        <span className={test.passed ? "marque-ok" : "marque-ko"}>
                          <Icon
                            nom={test.passed ? "coche" : "croix"}
                            taille={20}
                            titre={test.passed ? "Réussi" : "Échoué"}
                          />
                        </span>
                        <span>
                          <span className="nom-test">{test.name}</span>
                          {test.message && <span className="detail">{test.message}</span>}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}

                {exercice.kind === "python" && resultat.results.length === 0 && (
                  <pre className="sortie">{resultat.output}</pre>
                )}

                {exercice.kind === "python" && resultat.stdout?.trim() && (
                  <>
                    <h3>Ce que votre code a affiché</h3>
                    <pre className="sortie">{resultat.stdout}</pre>
                  </>
                )}

                {exercice.kind === "sql" && (
                  <>
                    <p className="discret">{resultat.output}</p>
                    {resultat.rows && (
                      <>
                        <h3>Votre résultat</h3>
                        <Tableau colonnes={resultat.columns} lignes={resultat.rows} />
                      </>
                    )}
                    {resultat.expected_rows && (
                      <>
                        <h3>Résultat attendu (début)</h3>
                        <Tableau lignes={resultat.expected_rows} />
                      </>
                    )}
                  </>
                )}

                {estQuiz && <p className="discret">{resultat.output}.</p>}

                {resultat.solution && (
                  <details className="repli">
                    <summary>Comparer avec une solution possible</summary>
                    <div className="listing">
                      <pre>
                        <code>{resultat.solution}</code>
                      </pre>
                    </div>
                  </details>
                )}
              </>
            )}
          </div>
        </section>
      </div>
    </article>
  );
}
