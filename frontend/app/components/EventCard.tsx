import Image from "next/image";

type EventCardProps = {
  data: {
    url: string;
    date: string;
    name: string;
    image: string;
    venue: string;
    address: string;
  };
};

export default function EventCard({ data }: EventCardProps) {
  // Format date to readable format
  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  // Format time
  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  return (
    <a
      href={data.url}
      target="_blank"
      rel="noopener noreferrer"
      className="w-[320px] flex-shrink-0 overflow-hidden rounded-2xl border border-pink-100 bg-white shadow-md transition hover:shadow-xl cursor-pointer mb-4"
    >
      {/* Event Image */}
      <div className="relative h-48 w-full overflow-hidden bg-gradient-to-br from-pink-100 to-purple-100">
        {data.image ? (
          <Image
            src={data.image}
            alt={data.name}
            fill
            className="object-cover"
            unoptimized
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <svg
              className="h-16 w-16 text-pink-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"
              />
            </svg>
          </div>
        )}
        {/* Date Badge */}
        <div className="absolute left-3 top-3 rounded-lg bg-white/95 px-3 py-2 backdrop-blur-sm shadow-md">
          <p className="text-xs font-semibold text-pink-600 uppercase">
            {formatDate(data.date).split(",")[0]}
          </p>
          <p className="text-lg font-bold text-gray-900">
            {new Date(data.date).getDate()}
          </p>
          <p className="text-xs text-gray-600">
            {new Date(data.date).toLocaleDateString("en-US", { month: "short" })}
          </p>
        </div>
      </div>

      {/* Event Info */}
      <div className="p-4">
        {/* Event Name */}
        <h3 className="mb-3 text-lg font-bold text-gray-900 line-clamp-2">
          {data.name}
        </h3>

        {/* Time */}
        <div className="mb-2 flex items-center gap-2">
          <svg
            className="h-4 w-4 flex-shrink-0 text-pink-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm font-medium text-gray-700">
            {formatTime(data.date)}
          </p>
        </div>

        {/* Venue */}
        <div className="flex items-start gap-2">
          <svg
            className="mt-0.5 h-4 w-4 flex-shrink-0 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          <p className="text-sm text-gray-600 line-clamp-2">{data.venue}</p>
        </div>
      </div>
    </a>
  );
}
