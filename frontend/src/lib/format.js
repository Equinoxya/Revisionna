// Mise en forme « à la française » : notes sur 20, dates, appréciations.

/** 0.725 -> « 14,5 » (arrondi au demi-point, virgule décimale). */
export function surVingt(score) {
  if (score === null || score === undefined) return null;
  const note = Math.round(score * 40) / 2;
  return note.toLocaleString("fr-FR", { maximumFractionDigits: 1 });
}

/** Appréciation du bulletin, selon l'avancement et la moyenne d'un cours. */
export function appreciation({ lessons_done, lessons_total, exercises_passed, exercises_total, average }) {
  const fait = lessons_done + exercises_passed;
  const total = lessons_total + exercises_total;
  if (fait === 0 && average === null) return "À commencer";
  if (total > 0 && fait === total) return "Chapitre bouclé, bravo";
  if (average === null) return "C'est parti";
  if (average >= 0.85) return "Très bien";
  if (average >= 0.7) return "Bon travail";
  if (average >= 0.5) return "En bonne voie";
  return "Des bases à revoir";
}

/** Appréciation d'une copie isolée. */
export function mention(score) {
  if (score >= 1) return "Très bien";
  if (score >= 0.8) return "Bien";
  if (score >= 0.6) return "Assez bien";
  if (score >= 0.4) return "Passable";
  return "À reprendre";
}

const JOUR = new Intl.DateTimeFormat("fr-FR", { weekday: "long", day: "numeric", month: "long" });
const COURT = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "short" });
const HEURE = new Intl.DateTimeFormat("fr-FR", { hour: "2-digit", minute: "2-digit" });

export function dateDuJour() {
  return JOUR.format(new Date());
}

/** « aujourd'hui 14:05 », « hier », « 3 nov. ». */
export function dateRelative(iso) {
  const date = new Date(iso);
  const minuit = new Date();
  minuit.setHours(0, 0, 0, 0);
  const ecart = Math.floor((minuit - new Date(date).setHours(0, 0, 0, 0)) / 86_400_000);
  if (ecart <= 0) return HEURE.format(date);
  if (ecart === 1) return "hier";
  return COURT.format(date);
}

/** « Données » -> « donnees » : sert de clé pour la couleur d'une catégorie. */
export function cle(texte) {
  return (texte || "autre")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-");
}

export function pluriel(nombre, singulier, plurielForme = `${singulier}s`) {
  return `${nombre} ${nombre > 1 ? plurielForme : singulier}`;
}

export function deuxChiffres(nombre) {
  return String(nombre).padStart(2, "0");
}

const NIVEAUX = { facile: 1, moyen: 2, difficile: 3 };

export function niveauDifficulte(difficulte) {
  return NIVEAUX[cle(difficulte)] ?? 1;
}
