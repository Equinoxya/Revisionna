import { useId, useState } from "react";

import Icon from "./Icon.jsx";

/** Champ de formulaire : libellé, aide, erreur reliée au champ pour les lecteurs d'écran. */
export default function Champ({ libelle, aide, erreur, type = "text", children, ...props }) {
  const id = useId();
  const [visible, setVisible] = useState(false);
  const secret = type === "password";
  const decrit = [aide || children ? `${id}-aide` : null, erreur ? `${id}-erreur` : null]
    .filter(Boolean)
    .join(" ");

  const champ = (
    <input
      id={id}
      type={secret && visible ? "text" : type}
      aria-invalid={erreur ? "true" : undefined}
      aria-describedby={decrit || undefined}
      {...props}
    />
  );

  return (
    <div className="champ">
      <label htmlFor={id}>{libelle}</label>
      {secret ? (
        <div className="avec-bouton">
          {champ}
          <button
            type="button"
            className="bouton-icone"
            onClick={() => setVisible(!visible)}
            aria-pressed={visible}
            aria-label={visible ? "Masquer le mot de passe" : "Afficher le mot de passe"}
            title={visible ? "Masquer" : "Afficher"}
          >
            <Icon nom="oeil" />
          </button>
        </div>
      ) : (
        champ
      )}
      {(aide || children) && (
        <div className="aide" id={`${id}-aide`}>
          {aide}
          {children}
        </div>
      )}
      {erreur && (
        <span className="erreur" id={`${id}-erreur`} role="alert">
          {erreur}
        </span>
      )}
    </div>
  );
}
