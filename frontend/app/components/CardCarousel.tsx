"use client";

import { useRef } from "react";
import RestaurantCard from "./RestaurantCard";
import FlightCard from "./FlightCard";
import AttractionCard from "./AttractionCard";
import EventCard from "./EventCard";
import HotelCard from "./HotelCard";

type Card = {
  type: string;
  id: string;
  data: any;
};

type CardCarouselProps = {
  cards: Card[];
};

export default function CardCarousel({ cards }: CardCarouselProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const scrollAmount = 320; // card width + gap
      const newScrollLeft =
        scrollRef.current.scrollLeft +
        (direction === "left" ? -scrollAmount : scrollAmount);
      scrollRef.current.scrollTo({
        left: newScrollLeft,
        behavior: "smooth",
      });
    }
  };

  if (!cards || cards.length === 0) return null;

  return (
    <div className="relative mt-3 w-full">
      {/* Left Arrow */}
      <button
        onClick={() => scroll("left")}
        className="absolute left-0 top-1/2 z-10 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-white shadow-lg transition hover:bg-gray-50 disabled:opacity-50"
        aria-label="Scroll left"
      >
        <svg
          className="h-6 w-6 text-gray-700"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
      </button>

      {/* Cards Container */}
      <div
        ref={scrollRef}
        className="flex gap-4 overflow-x-auto px-12 scrollbar-hide"
        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
      >
        {cards.map((card, index) => {
          // Use index as fallback to ensure unique keys
          const uniqueKey = `${card.type}-${card.id}-${index}`;
          
          if (card.type === "restaurant") {
            return <RestaurantCard key={uniqueKey} data={card.data} />;
          }
          if (card.type === "flight") {
            return <FlightCard key={uniqueKey} id={card.id} data={card.data} />;
          }
          if (card.type === "attraction") {
            return <AttractionCard key={uniqueKey} data={card.data} />;
          }
          if (card.type === "event") {
            return <EventCard key={uniqueKey} data={card.data} />;
          }
          if (card.type === "hotel") {
            return <HotelCard key={uniqueKey} data={card.data} />;
          }
          // Add more card types here in the future
          return null;
        })}
      </div>

      {/* Right Arrow */}
      <button
        onClick={() => scroll("right")}
        className="absolute right-0 top-1/2 z-10 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-white shadow-lg transition hover:bg-gray-50 disabled:opacity-50"
        aria-label="Scroll right"
      >
        <svg
          className="h-6 w-6 text-gray-700"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </button>
    </div>
  );
}
