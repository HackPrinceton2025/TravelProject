"use client";

import { useParams } from "next/navigation";

export default function GroupPage() {
  const params = useParams<{ groupId: string }>();
  const groupId = params?.groupId ?? "";

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Group: {groupId}</h1>
      <p className="text-gray-300">Welcome to the group dashboard.</p>
    </div>
  );
}


