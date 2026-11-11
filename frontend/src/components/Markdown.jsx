import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Rendu markdown commun aux lecons et aux enonces de TP. */
export default function Markdown({ children }) {
  return (
    <div className="markdown">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children || ""}</ReactMarkdown>
    </div>
  );
}
