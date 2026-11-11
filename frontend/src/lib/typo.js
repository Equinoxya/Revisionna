// Typographie française : pas de retour à la ligne avant « ; : ! ? » ni à
// l'intérieur des guillemets. On remplace l'espace ordinaire par une espace
// insécable (fine devant ; ! ?), uniquement dans le texte, jamais dans le code.

const FINE = " ";
const INSECABLE = " ";

export function typo(texte) {
  return texte
    .replace(/ ([;!?])/g, `${FINE}$1`)
    .replace(/ :(?=\s|$)/g, `${INSECABLE}:`)
    .replace(/« /g, `«${INSECABLE}`)
    .replace(/ »/g, `${INSECABLE}»`);
}

/** Extension remark : applique `typo` aux nœuds de texte (le code est d'un autre type). */
export function remarkTypo() {
  const parcourir = (noeud) => {
    if (noeud.type === "text") noeud.value = typo(noeud.value);
    noeud.children?.forEach(parcourir);
  };
  return parcourir;
}
