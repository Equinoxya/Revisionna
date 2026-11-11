import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

// Le choix est mémorisé dans le navigateur (localStorage). C'est un réglage
// d'affichage demandé par l'utilisateur : il ne sert à aucun suivi.
const CLE = "revisionna.theme";
const COULEUR_BARRE = { light: "#fcfbf7", dark: "#17231e" };
const sombreSysteme = window.matchMedia("(prefers-color-scheme: dark)");

function lireChoix() {
  try {
    const valeur = localStorage.getItem(CLE);
    return valeur === "light" || valeur === "dark" ? valeur : "auto";
  } catch {
    return "auto";
  }
}

function resoudre(choix) {
  if (choix === "auto") return sombreSysteme.matches ? "dark" : "light";
  return choix;
}

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [choix, setChoixEtat] = useState(lireChoix);
  const [theme, setTheme] = useState(() => resoudre(lireChoix()));

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", COULEUR_BARRE[theme]);
  }, [theme]);

  // En mode automatique, on suit les changements du système en direct.
  useEffect(() => {
    if (choix !== "auto") return undefined;
    const suivre = () => setTheme(resoudre("auto"));
    sombreSysteme.addEventListener("change", suivre);
    return () => sombreSysteme.removeEventListener("change", suivre);
  }, [choix]);

  const setChoix = useCallback((nouveau) => {
    try {
      if (nouveau === "auto") localStorage.removeItem(CLE);
      else localStorage.setItem(CLE, nouveau);
    } catch {
      // Stockage indisponible : le choix vaudra pour cette visite seulement.
    }
    setChoixEtat(nouveau);
    setTheme(resoudre(nouveau));
  }, []);

  const basculer = useCallback(() => {
    setChoix(theme === "dark" ? "light" : "dark");
  }, [theme, setChoix]);

  const valeur = useMemo(() => ({ theme, choix, setChoix, basculer }), [theme, choix, setChoix, basculer]);
  return <ThemeContext.Provider value={valeur}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const contexte = useContext(ThemeContext);
  if (!contexte) throw new Error("useTheme doit être utilisé dans un ThemeProvider");
  return contexte;
}
