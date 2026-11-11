import Icon from "./Icon.jsx";

/**
 * Question à choix unique, pour les leçons et les TP de type QCM.
 * Une fois corrigée (`resultat`), la bonne réponse est soulignée en vert, une
 * mauvaise réponse choisie est barrée, et le correcteur laisse un mot.
 */
export default function Quiz({ numero, question, choix, valeur, onChange, resultat, nom }) {
  const corrige = Boolean(resultat);
  const explication = resultat?.explanation || resultat?.message;

  return (
    <fieldset className="question" data-corrige={corrige ? "" : undefined}>
      <legend>
        {numero && <span className="numero">{numero}.</span>}
        {question}
      </legend>

      {corrige && (
        <span className={`en-marge ${resultat.passed ? "marque-ok" : "marque-ko"}`}>
          <Icon nom={resultat.passed ? "coche" : "croix"} taille={34} />
        </span>
      )}

      {choix.map((option) => {
        const choisie = valeur === option;
        const bonne = corrige && resultat.answer === option;
        const mauvaise = corrige && choisie && !resultat.passed;
        return (
          <label key={option} className={`choix${bonne ? " bonne" : ""}${mauvaise ? " mauvaise" : ""}`}>
            <input
              type="radio"
              name={nom}
              value={option}
              checked={choisie}
              onChange={() => onChange(option)}
              disabled={corrige}
            />
            <span>{option}</span>
            {bonne && (
              <span className="verdict marque-ok">
                <Icon nom="coche" taille={18} titre="Bonne réponse" />
              </span>
            )}
            {mauvaise && (
              <span className="verdict marque-ko">
                <Icon nom="croix" taille={18} titre="Mauvaise réponse" />
              </span>
            )}
          </label>
        );
      })}

      {corrige && (
        <p className="correction">
          <span className="cursive">{resultat.passed ? "Juste." : valeur ? "Faux." : "Sans réponse."}</span>
          {explication}
        </p>
      )}
    </fieldset>
  );
}
