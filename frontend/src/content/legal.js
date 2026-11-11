// Informations légales de VOTRE site : à compléter avant toute mise en ligne.
// Tant qu'un champ est vide, la page correspondante affiche « à compléter » en surligné.
// Le détail de ce qui est attendu est dans docs/conformite-rgpd.md.

export const EDITEUR = {
  // Site tenu par un particulier, à titre non professionnel : vous pouvez laisser
  // `nom` et `adresse` vides, À CONDITION d'avoir communiqué votre identité à
  // votre hébergeur. La page l'indiquera alors à votre place.
  nom: "",
  adresse: "",
  // Obligatoire : c'est par là qu'on vous écrit pour exercer ses droits.
  contact: "",
};

export const HEBERGEUR = {
  nom: "",        // raison sociale de l'entreprise dont les serveurs hébergent le site
  adresse: "",
  telephone: "",
  pays: "",       // pays où se trouvent les serveurs (ex. « France »)
};

// Durée de conservation des journaux techniques chez votre hébergeur
// (la CNIL recommande entre six mois et un an).
export const JOURNAUX_TECHNIQUES = "";

export const MISE_A_JOUR = "11 novembre 2026";
