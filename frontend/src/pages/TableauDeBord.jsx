import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../lib/api.js";
import { useAuth } from "../lib/AuthContext.jsx";

export default function TableauDeBord() {
  const { user } = useAuth();
  const [donnees, setDonnees] = useState(null);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    let annule = false;
    api("/me/dashboard")
      .then((data) => {
        if (!annule) setDonnees(data);
      })
      .catch((exception) => {
        if (!annule) setErreur(exception.message);
      });
    return () => {
      annule = true;
    };
  }, []);

  if (erreur) return <p className="alerte">{erreur}</p>;
  if (!donnees) return <p className="etat">Chargement...</p>;

  const { totals, courses, recent_submissions: recentes } = donnees;

  return (
    <section>
      <h1>Bonjour {user.username}</h1>
      <p className="sous-titre">Voici ou vous en etes.</p>

      <div className="stats">
        <div className="stat">
          <strong>{totals.lessons_done}</strong>
          <span>lecons terminees</span>
        </div>
        <div className="stat">
          <strong>{totals.exercises_passed}</strong>
          <span>TP reussis</span>
        </div>
        <div className="stat">
          <strong>{totals.submissions}</strong>
          <span>soumissions</span>
        </div>
      </div>

      <h2>Progression par cours</h2>
      <ul className="liste-progression">
        {courses.map((cours) => {
          const total = cours.lessons_total + cours.exercises_total;
          const fait = cours.lessons_done + cours.exercises_passed;
          const pourcentage = total ? Math.round((fait / total) * 100) : 0;
          return (
            <li key={cours.slug}>
              <Link to={`/cours/${cours.slug}`} className="ligne-progression">
                <span className="icone" aria-hidden="true">
                  {cours.icon}
                </span>
                <span className="titre">{cours.title}</span>
                <span className="barre">
                  <span className="jauge" style={{ width: `${pourcentage}%` }} />
                </span>
                <span className="pourcentage">{pourcentage}%</span>
              </Link>
            </li>
          );
        })}
      </ul>

      <h2>Dernieres soumissions</h2>
      {recentes.length === 0 ? (
        <p className="etat">
          Aucune soumission pour le moment. <Link to="/cours">Choisissez un cours</Link>.
        </p>
      ) : (
        <table className="tableau">
          <thead>
            <tr>
              <th>Exercice</th>
              <th>Resultat</th>
              <th>Score</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {recentes.map((soumission) => (
              <tr key={soumission.id}>
                <td>{soumission.exercise_title}</td>
                <td>
                  <span className={soumission.passed ? "badge-ok" : "badge-ko"}>
                    {soumission.passed ? "reussi" : "echec"}
                  </span>
                </td>
                <td>{Math.round(soumission.score * 100)}%</td>
                <td>{new Date(soumission.created_at).toLocaleString("fr-FR")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
