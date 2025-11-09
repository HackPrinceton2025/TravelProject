"use client";

import { useEffect, useMemo, useState } from "react";
import { PreferenceStatus, updatePreferences } from "../lib/api";

type Step = "interests" | "budget" | "departure" | "done";

type Props = {
  groupId: string;
  userId: string;
  status: PreferenceStatus;
  onUpdated: () => Promise<void> | void;
};

const getNextStep = (status: PreferenceStatus): Step => {
  if (!status.has_interests) return "interests";
  if (!status.has_budget) return "budget";
  if (!status.has_departure_city) return "departure";
  return "done";
};

export default function PreferenceOnboarding({
  groupId,
  userId,
  status,
  onUpdated,
}: Props) {
  const [currentStep, setCurrentStep] = useState<Step>(getNextStep(status));
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setCurrentStep(getNextStep(status));
    setInputValue("");
    setError(null);
  }, [status]);

  const prompt = useMemo(() => {
    switch (currentStep) {
      case "interests":
        return {
          title: "What kind of trip are you dreaming about?",
          helper: "Add a few interests separated by commas (e.g., Beaches, Food, Hiking). Only you and the AI see this.",
          placeholder: "e.g., Beaches, Museums, Food Markets",
          inputType: "text" as const,
        };
      case "budget":
        return {
          title: "What's your ideal budget (USD)?",
          helper: "Give a single number so I can suggest the right options for you.",
          placeholder: "e.g., 2500",
          inputType: "number" as const,
        };
      case "departure":
        return {
          title: "Where will you be departing from?",
          helper: "Knowing your home airport helps me find the best flights.",
          placeholder: "e.g., New York, NY",
          inputType: "text" as const,
        };
      default:
        return null;
    }
  }, [currentStep]);

  if (currentStep === "done" || !prompt) {
    return null;
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    try {
      setSubmitting(true);

      if (currentStep === "interests") {
        const interests = inputValue
          .split(",")
          .map((item) => item.trim())
          .filter((item) => item.length > 0);
        if (!interests.length) {
          setError("Add at least one interest so I know what to plan.");
          return;
        }
        await updatePreferences({
          group_id: groupId,
          user_id: userId,
          interests,
        });
      } else if (currentStep === "budget") {
        const numericValue = Number(inputValue);
        if (!Number.isFinite(numericValue) || numericValue <= 0) {
          setError("Enter a number greater than zero.");
          return;
        }
        await updatePreferences({
          group_id: groupId,
          user_id: userId,
          budget_max: Math.round(numericValue),
        });
      } else if (currentStep === "departure") {
        const city = inputValue.trim();
        if (!city) {
          setError("Please provide the city you'll depart from.");
          return;
        }
        await updatePreferences({
          group_id: groupId,
          user_id: userId,
          departure_city: city,
        });
      }

      await onUpdated();
      setInputValue("");
    } catch (err) {
      console.error("Failed to update preferences", err);
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto mb-6 w-full max-w-5xl rounded-3xl border border-purple-100 bg-gradient-to-br from-purple-50 via-white to-pink-50 p-6 shadow-lg">
      <div className="flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.35em] text-purple-400">
        <span>AI Travel Agent</span>
        <span className="text-xs font-normal tracking-normal text-purple-300">
          only visible to you
        </span>
      </div>
      <h3 className="mt-4 text-2xl font-semibold text-gray-900">{prompt.title}</h3>
      <p className="mt-2 text-sm text-gray-600">{prompt.helper}</p>

      <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
        <input
          type={prompt.inputType === "number" ? "number" : "text"}
          inputMode={prompt.inputType === "number" ? "numeric" : "text"}
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          placeholder={prompt.placeholder}
          className="w-full rounded-2xl border border-purple-200 bg-white px-4 py-3 text-sm text-gray-800 placeholder:text-gray-400 focus:border-purple-400 focus:outline-none"
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="rounded-full bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-2 text-sm font-semibold text-white shadow-md shadow-purple-200 transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Saving…" : "Save & Continue"}
          </button>
          <span className="text-xs text-gray-400">
            Step {currentStep === "interests" ? 1 : currentStep === "budget" ? 2 : 3}{" "}
            of 3
          </span>
        </div>
      </form>
    </div>
  );
}
