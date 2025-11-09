import Image from "next/image";

type HotelCardProps = {
  data: {
    name: string;
    image?: string;
    price: number;
    stars?: number;
    nights?: number;
    rating?: number;
    check_in?: string;
    currency: string;
    hotel_id: number;
    location?: string;
    check_out?: string;
    price_unit?: string;
    total_price?: number;
    review_count?: number;
    review_score?: number;
    review_score_word?: string;
    website?: string;
  };
};

export default function HotelCard({ data }: HotelCardProps) {
  // Format date to readable format
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  const CardWrapper = data.website ? "a" : "div";
  const cardProps = data.website
    ? { href: data.website, target: "_blank", rel: "noopener noreferrer" }
    : {};

  return (
    <CardWrapper
      {...cardProps}
      className={`w-[320px] flex-shrink-0 overflow-hidden rounded-2xl border border-indigo-100 bg-white shadow-md transition mb-4 ${
        data.website ? "hover:shadow-xl cursor-pointer" : "hover:shadow-xl"
      }`}
    >
      {/* Hotel Image */}
      <div className="relative h-44 w-full overflow-hidden bg-gradient-to-br from-indigo-100 to-blue-100">
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
              className="h-16 w-16 text-indigo-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
              />
            </svg>
          </div>
        )}
        {/* Stars Badge */}
        {data.stars && (
          <div className="absolute right-3 top-3 rounded-lg bg-white/95 px-2 py-1 backdrop-blur-sm shadow-md">
            <div className="flex items-center gap-1">
              {Array.from({ length: data.stars }).map((_, i) => (
                <svg
                  key={i}
                  className="h-3 w-3 text-yellow-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Hotel Info */}
      <div className="p-4">
        {/* Hotel Name */}
        <h3 className="mb-3 text-lg font-bold text-gray-900 line-clamp-2">
          {data.name}
        </h3>

        {/* Review Score */}
        {data.review_score && (
          <div className="mb-3 flex items-center gap-2">
            <div className="rounded-lg bg-indigo-600 px-2 py-1">
              <span className="text-sm font-bold text-white">
                {data.review_score.toFixed(1)}
              </span>
            </div>
            {data.review_score_word && (
              <span className="text-sm font-semibold text-gray-700">
                {data.review_score_word}
              </span>
            )}
            {data.review_count && (
              <span className="text-xs text-gray-500">
                ({data.review_count.toLocaleString()} reviews)
              </span>
            )}
          </div>
        )}

        {/* Price */}
        <div className="mb-3">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-indigo-600">
              {data.currency} {data.price}
            </span>
            {data.price_unit && (
              <span className="text-sm text-gray-500">/ {data.price_unit}</span>
            )}
          </div>
          {data.nights && data.total_price && (
            <p className="text-xs text-gray-600 mt-1">
              {data.nights} {data.nights === 1 ? "night" : "nights"} · Total: {data.currency} {data.total_price}
            </p>
          )}
        </div>

        {/* Check-in/out Dates */}
        {data.check_in && data.check_out && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <svg
              className="h-4 w-4 text-indigo-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span>
              {formatDate(data.check_in)} - {formatDate(data.check_out)}
            </span>
          </div>
        )}
      </div>
    </CardWrapper>
  );
}
