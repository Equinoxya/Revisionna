import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { remarkTypo } from "../lib/typo.js";

// Le HTML brut n'est pas interprété (comportement par défaut de react-markdown) :
// un contenu de cours ne peut pas injecter de script.
const COMPOSANTS = {
  table: ({ children }) => (
    <div className="defilable">
      <table>{children}</table>
    </div>
  ),
  pre: ({ children }) => (
    <div className="listing">
      <pre>{children}</pre>
    </div>
  ),
};

/** Rendu markdown commun aux leçons et aux énoncés de TP. */
export default function Markdown({ children }) {
  return (
    <div className="prose">
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkTypo]} components={COMPOSANTS}>
        {children || ""}
      </ReactMarkdown>
    </div>
  );
}
