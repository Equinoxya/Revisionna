import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../lib/api.js";

export default function Catalogue() {
  const [cours, setCours] = useState(null);
  const [erreur, setErreur] = useState(null);
  const [filtre, setFiltre] = useState("tous");

  useEffect(() => {
    let annule = false;
    api("/courses")
      .then((data) => {
        if (!annule) setCours(data.courses);
      })
      .catch((exception) => {
        if (!annule) setErreur(exception.message);
      });
    return () => {
      annule = true;
    };
  }, []);

  if (erreur) return <p className="alerte">{erreur}</p>;
  if (!cours) return <p className="etat">Chargement...</p>;

  const categories = ["tous", ...new Set(cours.map((c) => c.category))];
  const visibles = filtre === "tous" ? cours : cours.filter((c) => c.category === filtre);

  return (
    <section>
      <h1>Catalogue</h1>
      <p className="sous-titre">{cours.length} cours, chacun avec ses lecons et ses TP.</p>

      <div className="filtres">
        {categories.map((categorie) => (
          <button
            key={categorie}
            type="button"
            className={categorie === filtre ? "puce active" : "puce"}
            onClick={() => setFiltre(categorie)}
          >
            {categorie}
          </button>
        ))}
      </div>

      <div className="grille">
        {visibles.map((item) => (
          <Link key={item.slug} to={`/cours/${item.slug}`} className="carte">
            <span className="icone-carte" aria-hidden="true">
              {item.icon}
            </span>
            <h3>{item.title}</h3>
            <p>{item.summary}</p>
            <footer>
              <span>{item.lessons_count} lecons</span>
              <span>{item.exercises_count} TP</span>
              <span className="niveau">{item.level}</span>
            </footer>
          </Link>
        ))}
      </div>
    </section>
  );
}
