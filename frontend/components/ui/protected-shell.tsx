"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { getAccessToken } from "@/lib/auth";

export function ProtectedShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    if (!getAccessToken()) {
      router.replace("/login");
    }
  }, [router]);

  return <>{children}</>;
}

