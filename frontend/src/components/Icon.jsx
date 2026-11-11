// Petites icônes au trait, dessinées pour l'application (aucune dépendance, aucun emoji).

const TRACES = {
  // Coche et croix du correcteur : un seul geste, volontairement pas tout à fait droit.
  coche: <path d="M4.5 12.8c2 1.7 3.3 3.3 4.6 5.4C11.7 12.9 15 8.2 19.8 4.8" />,
  croix: (
    <>
      <path d="M5.5 5.2c3.9 3.9 8.3 8.6 13 13.9" />
      <path d="M18.8 4.9C14.2 9.6 9.9 14.1 5.2 19.2" />
    </>
  ),
  soleil: (
    <>
      <circle cx="12" cy="12" r="4.2" />
      <path d="M12 2.5v2.3M12 19.2v2.3M2.5 12h2.3M19.2 12h2.3M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6" />
    </>
  ),
  lune: <path d="M19.5 14.6A8 8 0 0 1 9.4 4.5a8 8 0 1 0 10.1 10.1z" />,
  gauche: <path d="M14.5 5.5 8 12l6.5 6.5" />,
  droite: <path d="M9.5 5.5 16 12l-6.5 6.5" />,
  telecharger: <path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19.5h14" />,
  oeil: (
    <>
      <path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z" />
      <circle cx="12" cy="12" r="2.8" />
    </>
  ),
};

export default function Icon({ nom, taille = 20, titre, className }) {
  return (
    <svg
      className={className}
      width={taille}
      height={taille}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.1"
      strokeLinecap="round"
      strokeLinejoin="round"
      role={titre ? "img" : undefined}
      aria-label={titre}
      aria-hidden={titre ? undefined : true}
      focusable="false"
    >
      {TRACES[nom]}
    </svg>
  );
}
