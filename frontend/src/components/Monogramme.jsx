import { cle } from "../lib/format.js";

/** L'onglet d'un cours : ses initiales, et la couleur de sa famille. */
export default function Monogramme({ cours, grand = false }) {
  const classes = ["monogramme", `cat-${cle(cours.category)}`];
  if (grand) classes.push("grand");
  return (
    <span className={classes.join(" ")} aria-hidden="true">
      {cours.icon || cours.title.slice(0, 2)}
    </span>
  );
}
