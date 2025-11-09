"use client";

import { useState } from "react";

type RestaurantData = {
  name: string;
  cuisine: string;
  rating: number;
  price_level: string;
  address: string;
  image?: string;
  open_now?: boolean;
  total_ratings?: number;
  location?: {
    lat: number;
    lng: number;
  };
};

type RestaurantCardProps = {
  data: RestaurantData;
};

export default function RestaurantCard({ data }: RestaurantCardProps) {
  const [imageError, setImageError] = useState(false);

  return (
    <div className="flex min-w-[300px] max-w-[300px] flex-col overflow-hidden rounded-2xl border border-purple-100 bg-white shadow-lg transition hover:shadow-xl">
      {/* Restaurant Image */}
      <div className="relative h-40 w-full overflow-hidden bg-gradient-to-br from-purple-100 to-pink-100">
        {data.image && !imageError ? (
          <img
            src={data.image}
            alt={data.name}
            className="h-full w-full object-cover"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <svg
              className="h-16 w-16 text-purple-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              />
            </svg>
          </div>
        )}
        {/* Status Badge */}
        {data.open_now !== undefined && (
          <div className="absolute right-2 top-2">
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                data.open_now
                  ? "bg-green-500 text-white"
                  : "bg-red-500 text-white"
              }`}
            >
              {data.open_now ? "Open" : "Closed"}
            </span>
          </div>
        )}
      </div>

      {/* Restaurant Info */}
      <div className="flex flex-col gap-3 p-4">
        {/* Name and Price */}
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-bold text-gray-900">{data.name}</h3>
          <span className="text-sm font-semibold text-purple-600">
            {data.price_level}
          </span>
        </div>

        {/* Cuisine */}
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-purple-50 px-3 py-1 text-xs font-medium text-purple-700">
            {data.cuisine}
          </span>
        </div>

        {/* Rating */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <svg
              className="h-5 w-5 text-yellow-400"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="font-semibold text-gray-900">{data.rating}</span>
          </div>
          {data.total_ratings && (
            <span className="text-sm text-gray-500">
              ({data.total_ratings.toLocaleString()})
            </span>
          )}
        </div>

        {/* Address */}
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
          <p className="text-sm text-gray-600">{data.address}</p>
        </div>
      </div>
    </div>
  );
}
