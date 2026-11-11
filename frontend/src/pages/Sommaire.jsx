import { Link } from "react-router-dom";

import Monogramme from "../components/Monogramme.jsx";
import { cle, deuxChiffres, pluriel } from "../lib/format.js";
import { useApi } from "../lib/useApi.js";

/** Regroupe les cours par catégorie, en gardant l'ordre du programme. */
function parParties(cours) {
  const parties = [];
  for (const item of cours) {
    let partie = parties.find((p) => p.nom === item.category);
    if (!partie) {
      partie = { nom: item.category, cours: [] };
      parties.push(partie);
    }
    partie.cours.push(item);
  }
  return parties;
}

export default function Sommaire() {
  const { donnees, erreur } = useApi("/courses");

  if (erreur) return <p className="message erreur">{erreur}</p>;
  if (!donnees) return <p className="etat">Ouverture du sommaire…</p>;

  const cours = donnees.courses;
  const lecons = cours.reduce((somme, c) => somme + c.lessons_count, 0);
  const tp = cours.reduce((somme, c) => somme + c.exercises_count, 0);

  return (
    <>
      <h1>Sommaire</h1>
      <p className="chapeau">
        {pluriel(cours.length, "matière")}, {pluriel(lecons, "leçon")}, {tp} TP. Dans l&apos;ordre
        du programme, mais rien n&apos;oblige à le suivre.
      </p>

      {parParties(cours).map((partie) => (
        <section className={`partie cat-${cle(partie.nom)}`} key={partie.nom}>
          <h2>
            <span className="onglet" aria-hidden="true" />
            {partie.nom}
          </h2>
          <ol className="sommaire">
            {partie.cours.map((item) => (
              <li key={item.slug}>
                <Link to={`/cours/${item.slug}`}>
                  <span className="numero" aria-hidden="true">
                    {deuxChiffres(item.position + 1)}
                  </span>
                  <Monogramme cours={item} />
                  <span className="titre-cours">{item.title}</span>
                  <span className="resume">{item.summary}</span>
                  <span className="infos">
                    <span>{pluriel(item.lessons_count, "leçon")}</span>
                    <span>{item.exercises_count} TP</span>
                    <span>niveau {item.level}</span>
                    {item.lessons_done > 0 && (
                      <span className="avance">
                        {item.lessons_done === item.lessons_count
                          ? "leçons terminées"
                          : `${pluriel(item.lessons_done, "leçon")} faite${item.lessons_done > 1 ? "s" : ""}`}
                      </span>
                    )}
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </section>
      ))}
    </>
  );
}
