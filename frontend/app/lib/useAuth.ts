"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getSession, getCurrentUser } from "./auth";

export function useAuth(redirectTo = "/") {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const session = await getSession();
      if (!session) {
        router.push(redirectTo);
        return;
      }
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error("Auth check failed:", error);
      router.push(redirectTo);
    } finally {
      setLoading(false);
    }
  };

  return { user, loading };
}

