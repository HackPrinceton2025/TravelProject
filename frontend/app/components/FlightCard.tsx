import Image from "next/image";

type FlightCardProps = {
  id: string;
  data: {
    price: number;
    stops: number;
    origin: string;
    airline: string;
    currency: string;
    duration: number;
    cabin_class: string;
    destination: string;
    airline_logo: string;
    arrival_time: string;
    booking_token: string;
    flight_number: string;
    departure_date: string;
    departure_time: string;
  };
};

export default function FlightCard({ id, data }: FlightCardProps) {
  // Format time from ISO string to HH:MM
  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  };

  // Format duration from hours to "Xh Ym"
  const formatDuration = (hours: number) => {
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return `${h}h ${m}m`;
  };

  // Format date to "Mon DD"
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="w-[340px] flex-shrink-0 rounded-2xl border border-blue-100 bg-white p-5 shadow-md transition hover:shadow-lg mb-4">
      {/* Airline Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative h-10 w-10 overflow-hidden rounded-lg bg-gray-50">
            <Image
              src={data.airline_logo}
              alt={data.airline}
              fill
              className="object-contain p-1"
              unoptimized
            />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900">{data.airline}</p>
            <p className="text-xs text-gray-500">{data.flight_number}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-blue-600">
            {data.currency} {data.price.toFixed(2)}
          </p>
          <p className="text-xs text-gray-500">{data.cabin_class}</p>
        </div>
      </div>

      {/* Flight Route */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          {/* Departure */}
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{data.origin}</p>
            <p className="text-sm font-semibold text-gray-700">
              {formatTime(data.departure_time)}
            </p>
            <p className="text-xs text-gray-500">
              {formatDate(data.departure_date)}
            </p>
          </div>

          {/* Duration & Stops */}
          <div className="flex-1 px-4">
            <div className="relative">
              <div className="h-0.5 w-full bg-gradient-to-r from-blue-400 to-purple-400"></div>
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white px-2">
                <svg
                  className="h-4 w-4 text-blue-500"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </div>
            </div>
            <p className="mt-1 text-center text-xs text-gray-500">
              {formatDuration(data.duration)}
            </p>
            <p className="text-center text-xs font-medium text-gray-600">
              {data.stops === 0 ? "Direct" : `${data.stops} stop${data.stops > 1 ? "s" : ""}`}
            </p>
          </div>

          {/* Arrival */}
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{data.destination}</p>
            <p className="text-sm font-semibold text-gray-700">
              {formatTime(data.arrival_time)}
            </p>
            <p className="text-xs text-gray-500">
              {formatDate(data.arrival_time)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
