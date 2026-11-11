import { niveauDifficulte } from "../lib/format.js";

/** Difficulté d'un TP : le mot, doublé de trois points. */
export default function Difficulte({ valeur }) {
  const niveau = niveauDifficulte(valeur);
  return (
    <span className="difficulte">
      <span className="points" aria-hidden="true">
        {[1, 2, 3].map((rang) => (
          <i key={rang} className={rang <= niveau ? "plein" : undefined} />
        ))}
      </span>
      {valeur}
    </span>
  );
}
