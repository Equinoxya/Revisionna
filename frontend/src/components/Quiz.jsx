/** Question a choix unique, reutilisee dans les lecons et les exercices quiz. */
export default function Quiz({ question, choix, valeur, onChange, resultat, nom }) {
  const etat = resultat ? (resultat.passed ? "juste" : "faux") : "";

  return (
    <fieldset className={`quiz ${etat}`}>
      <legend>{question}</legend>

      {choix.map((option) => (
        <label key={option} className="choix">
          <input
            type="radio"
            name={nom}
            value={option}
            checked={valeur === option}
            onChange={() => onChange(option)}
            disabled={Boolean(resultat)}
          />
          <span>{option}</span>
        </label>
      ))}

      {resultat && (
        <p className="retour">
          {resultat.passed ? "Correct. " : `Incorrect. ${resultat.answer ? `Reponse : ${resultat.answer}. ` : ""}`}
          {resultat.message || resultat.explanation}
        </p>
      )}
    </fieldset>
  );
}
