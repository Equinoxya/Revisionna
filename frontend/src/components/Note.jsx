import { surVingt } from "../lib/format.js";

// Tracé d'un cercle fait à la main : il ne se referme pas tout à fait.
const CERCLE =
  "M52 6C31 3 8 11 5 27c-3 15 14 26 43 27 30 1 49-9 48-26C95 12 74 4 44 7";

/** Une note sur 20, entourée au stylo rouge comme en haut d'une copie. */
export default function Note({ score, grande = false, libelle }) {
  const valeur = surVingt(score);
  if (valeur === null) return null;

  return (
    <span className={grande ? "note grande" : "note"} role="img" aria-label={`${libelle ?? "Note"} : ${valeur} sur 20`}>
      <svg viewBox="0 0 100 60" preserveAspectRatio="none" aria-hidden="true" focusable="false">
        <path d={CERCLE} pathLength="1" vectorEffect="non-scaling-stroke" />
      </svg>
      <span className="valeur" aria-hidden="true">
        {valeur}/20
      </span>
    </span>
  );
}
