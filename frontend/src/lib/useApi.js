import { useEffect, useState } from "react";

import { api } from "./api.js";

/** Charge une ressource de l'API. Renvoie `{ donnees, erreur }` ; `donnees` vaut null pendant le chargement. */
export function useApi(chemin) {
  const [etat, setEtat] = useState({ chemin, donnees: null, erreur: null });

  useEffect(() => {
    let annule = false;
    api(chemin)
      .then((donnees) => {
        if (!annule) setEtat({ chemin, donnees, erreur: null });
      })
      .catch((exception) => {
        if (!annule) setEtat({ chemin, donnees: null, erreur: exception.message });
      });
    return () => {
      annule = true;
    };
  }, [chemin]);

  // Tant que la réponse affichée concerne une autre adresse, on est en chargement.
  return etat.chemin === chemin ? etat : { chemin, donnees: null, erreur: null };
}
