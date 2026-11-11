import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api } from "../lib/api.js";

export default function Cours() {
  const { coursSlug } = useParams();
  const [cours, setCours] = useState(null);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    let annule = false;
    setCours(null);
    api(`/courses/${coursSlug}`)
      .then((data) => {
        if (!annule) setCours(data.course);
      })
      .catch((exception) => {
        if (!annule) setErreur(exception.message);
      });
    return () => {
      annule = true;
    };
  }, [coursSlug]);

  if (erreur) return <p className="alerte">{erreur}</p>;
  if (!cours) return <p className="etat">Chargement...</p>;

  return (
    <section>
      <Link to="/cours" className="retour-lien">
        &larr; Catalogue
      </Link>

      <h1>
        <span aria-hidden="true">{cours.icon}</span> {cours.title}
      </h1>
      <p className="sous-titre">{cours.summary}</p>

      <div className="deux-colonnes">
        <div>
          <h2>Lecons interactives</h2>
          <ol className="liste-lecons">
            {cours.lessons.map((lecon) => (
              <li key={lecon.slug}>
                <Link to={`/cours/${cours.slug}/lecons/${lecon.slug}`}>
                  <span className={lecon.done ? "pastille faite" : "pastille"} aria-hidden="true" />
                  <span className="titre">{lecon.title}</span>
                  <span className="duree">{lecon.duration_min} min</span>
                </Link>
              </li>
            ))}
          </ol>
        </div>

        <div>
          <h2>Travaux pratiques</h2>
          <ol className="liste-lecons">
            {cours.exercises.map((exercice) => (
              <li key={exercice.slug}>
                <Link to={`/cours/${cours.slug}/exercices/${exercice.slug}`}>
                  <span className="pastille type" aria-hidden="true">
                    {exercice.kind === "sql" ? "SQL" : exercice.kind === "quiz" ? "QCM" : "PY"}
                  </span>
                  <span className="titre">{exercice.title}</span>
                  <span className="duree">{exercice.difficulty}</span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
