import { useEffect, useState } from "react";

import { api } from "./api.js";

// Informations publiques du serveur (fournisseur d'IA, règles d'inscription,
// durées de conservation). Chargées une seule fois pour toute l'application.
const DEFAUT = {
  ai_provider: "offline",
  ai_external: false,
  invite_required: false,
  terms_version: "",
  password_min_length: 12,
  session_hours: 12,
  inactive_account_months: 24,
  activity_retention_days: 180,
};

let promesse = null;

function charger() {
  if (!promesse) {
    promesse = api("/meta").catch(() => {
      promesse = null; // on réessaiera à la prochaine demande
      return DEFAUT;
    });
  }
  return promesse;
}

export function useMeta() {
  const [meta, setMeta] = useState(DEFAUT);
  useEffect(() => {
    let annule = false;
    charger().then((data) => {
      if (!annule) setMeta({ ...DEFAUT, ...data });
    });
    return () => {
      annule = true;
    };
  }, []);
  return meta;
}
