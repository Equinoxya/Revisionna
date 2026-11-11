import { Link, useParams } from "react-router-dom";

import Difficulte from "../components/Difficulte.jsx";
import Icon from "../components/Icon.jsx";
import Monogramme from "../components/Monogramme.jsx";
import { deuxChiffres } from "../lib/format.js";
import { useApi } from "../lib/useApi.js";

const GENRES = { python: "Python", sql: "SQL", quiz: "QCM" };

export default function Cours() {
  const { coursSlug } = useParams();
  const { donnees, erreur } = useApi(`/courses/${coursSlug}`);

  if (erreur) return <p className="message erreur">{erreur}</p>;
  if (!donnees) return <p className="etat">Ouverture du chapitre…</p>;

  const cours = donnees.course;

  return (
    <>
      <Link to="/cours" className="fil">
        <Icon nom="gauche" taille={16} /> Sommaire
      </Link>

      <div className="tete-cours">
        <Monogramme cours={cours} grand />
        <div>
          <div className="sur-titre">
            Chapitre {deuxChiffres(cours.position + 1)} · {cours.category} · niveau {cours.level}
          </div>
          <h1>{cours.title}</h1>
        </div>
      </div>
      <p className="chapeau">{cours.summary}</p>

      <div className="deux-colonnes">
        <section>
          <h2>Leçons</h2>
          <ol className="liste-travail">
            {cours.lessons.map((lecon) => (
              <li key={lecon.slug}>
                <Link to={`/cours/${cours.slug}/lecons/${lecon.slug}`}>
                  <span className={lecon.done ? "pastille faite" : "pastille"}>
                    {lecon.done && <Icon nom="coche" taille={15} titre="Leçon terminée" />}
                  </span>
                  <span className="titre-item">{lecon.title}</span>
                  <span className="duree">{lecon.duration_min} min</span>
                </Link>
              </li>
            ))}
          </ol>
        </section>

        <section>
          <h2>Travaux pratiques</h2>
          <ol className="liste-travail">
            {cours.exercises.map((exercice) => (
              <li key={exercice.slug}>
                <Link to={`/cours/${cours.slug}/exercices/${exercice.slug}`}>
                  <span className="etiquette">{GENRES[exercice.kind] ?? exercice.kind}</span>
                  <span className="titre-item">{exercice.title}</span>
                  <Difficulte valeur={exercice.difficulty} />
                </Link>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </>
  );
}
