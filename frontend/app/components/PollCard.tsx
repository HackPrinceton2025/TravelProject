type Props = {
  question: string;
  options: string[];
};

export default function PollCard({ question, options }: Props) {
  return (
    <div className="border border-gray-700 rounded p-4">
      <h3 className="font-semibold mb-2">{question}</h3>
      <ul className="space-y-2">
        {options.map((opt) => (
          <li key={opt} className="flex items-center gap-2">
            <button className="bg-gray-800 border border-gray-700 rounded px-2 py-1">
              Vote
            </button>
            <span>{opt}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}


