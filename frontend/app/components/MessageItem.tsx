type Props = {
  sender: string;
  content: string;
};

export default function MessageItem({ sender, content }: Props) {
  return (
    <div className="flex flex-col gap-1">
      <div className="text-sm text-gray-400">{sender}</div>
      <div className="bg-gray-800 border border-gray-700 rounded px-3 py-2">
        {content}
      </div>
    </div>
  );
}


