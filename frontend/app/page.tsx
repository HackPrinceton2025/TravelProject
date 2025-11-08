"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, signOut } from "./lib/auth";
import AuthModal from "./components/AuthModal";

export default function HomePage() {
  const router = useRouter();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error("Error checking user:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAuthSuccess = () => {
    setIsAuthModalOpen(false);
    checkUser();
  };

  const handleSignOut = async () => {
    await signOut();
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-blue-600 text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">✈️</span>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-orange-500 bg-clip-text text-transparent">
              TripSmith
            </h1>
          </div>
          <nav className="flex items-center gap-4">
            {user ? (
              <>
                <span className="text-gray-700">Hi, {user.user_metadata?.name || user.email}!</span>
                <button
                  onClick={() => router.push("/groups")}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  My Groups
                </button>
                <button
                  onClick={handleSignOut}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsAuthModalOpen(true)}
                className="px-6 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-md hover:shadow-lg"
              >
                Get Started
              </button>
            )}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-blue-500 to-orange-500 bg-clip-text text-transparent">
            Plan Your Perfect Group Trip
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Collaborate with friends, get AI-powered recommendations, and make travel planning
            effortless. Your adventure starts here.
          </p>
          {!user && (
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => setIsAuthModalOpen(true)}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-lg font-semibold rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                Start Planning
              </button>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-2">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">Group Chat</h3>
            <p className="text-gray-600">
              Real-time collaboration with your travel companions. Discuss, decide, and plan
              together seamlessly.
            </p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-2">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">AI Assistant</h3>
            <p className="text-gray-600">
              Get personalized recommendations for flights, hotels, restaurants, and activities
              based on your group's preferences.
            </p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-2">
            <div className="text-4xl mb-4">🗳️</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">Vote & Decide</h3>
            <p className="text-gray-600">
              Use polls and voting to reach group consensus on destinations, dates, and
              activities.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white/60 backdrop-blur-sm rounded-3xl p-12 shadow-xl">
          <h3 className="text-3xl font-bold text-center mb-12 text-gray-800">How It Works</h3>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h4 className="font-semibold text-lg mb-2">Create a Group</h4>
              <p className="text-gray-600 text-sm">Start a new trip and invite your friends</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h4 className="font-semibold text-lg mb-2">Set Preferences</h4>
              <p className="text-gray-600 text-sm">Share your budget, dates, and interests</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h4 className="font-semibold text-lg mb-2">Chat & Plan</h4>
              <p className="text-gray-600 text-sm">Discuss and get AI recommendations</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                4
              </div>
              <h4 className="font-semibold text-lg mb-2">Book & Go</h4>
              <p className="text-gray-600 text-sm">Finalize plans and start your adventure</p>
            </div>
          </div>
        </div>
      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}



