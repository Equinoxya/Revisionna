import { useTheme } from "../lib/theme.jsx";
import Icon from "./Icon.jsx";

/** Bascule cahier (clair) / tableau noir (sombre). */
export default function ThemeToggle() {
  const { theme, basculer } = useTheme();
  const versSombre = theme !== "dark";
  const libelle = versSombre ? "Passer au tableau noir (mode sombre)" : "Revenir au cahier (mode clair)";

  return (
    <button type="button" className="bouton-icone" onClick={basculer} aria-label={libelle} title={libelle}>
      <Icon nom={versSombre ? "lune" : "soleil"} />
    </button>
  );
}
