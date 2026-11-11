/** Texte court avec du `code` entre accents graves (questions, réponses, explications). */
export default function Texte({ children }) {
  const morceaux = String(children ?? "").split("`");
  if (morceaux.length < 3) return children ?? null;
  return morceaux.map((morceau, index) =>
    index % 2 === 1 ? <code key={index}>{morceau}</code> : morceau,
  );
}
