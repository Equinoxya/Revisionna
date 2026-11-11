/** Rend la valeur si elle est renseignée, sinon un rappel bien visible pour l'éditeur du site. */
export default function ACompleter({ valeur, quoi }) {
  if (valeur) return valeur;
  return <mark className="a-completer">à compléter : {quoi}</mark>;
}
