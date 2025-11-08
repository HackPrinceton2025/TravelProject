import "./styles/globals.css";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white min-h-screen">
        <header className="p-4 text-xl font-bold border-b border-gray-700">
          TravelProject
        </header>
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}


