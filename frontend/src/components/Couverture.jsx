import { Link } from "react-router-dom";

import { LiensLegaux } from "./Layout.jsx";
import ThemeToggle from "./ThemeToggle.jsx";

const MATIERES = [
  "Python", "Flask", "Django", "React", "SQL", "NoSQL",
  "Machine learning", "Intégration de l'IA", "Docker", "CI/CD", "Déploiement",
];

/** Mise en page des écrans de connexion et d'inscription : un cahier ouvert. */
export default function Couverture({ children }) {
  return (
    <div className="couverture">
      <div className="page-gauche seyes">
        <Link to="/" className="titre-cahier">
          Revisionna
        </Link>
        <p className="accroche">
          Le cahier de révision de l&apos;année : des leçons à faire, des{" "}
          <span className="surligne">TP corrigés</span> sur-le-champ.
        </p>
        <ul className="matieres" aria-label="Matières au programme">
          {MATIERES.map((matiere) => (
            <li key={matiere}>{matiere}</li>
          ))}
        </ul>
      </div>

      <main className="page-droite">
        <div className="haut-droite">
          <ThemeToggle />
        </div>
        <div className="formulaire-auth">{children}</div>
        <nav className="liens-legaux" aria-label="Informations légales">
          <LiensLegaux />
        </nav>
      </main>
    </div>
  );
}
