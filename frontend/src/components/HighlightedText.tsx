export default function HighlightedText({ text, terms }: { text: string; terms: string[] }) {
  if (!terms.length) return <p className="whitespace-pre-wrap">{text}</p>;
  
  // Escape regex special characters
  const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp("(" + terms.map(esc).join("|") + ")", "gi");

  return (
    <p className="whitespace-pre-wrap leading-relaxed text-sm">
      {text.split(re).map((part, i) => 
        i % 2 === 1 ? (
          <mark key={i} className="rounded bg-warn/30 px-0.5 text-warn">{part}</mark>
        ) : (
          part
        )
      )}
    </p>
  );
}