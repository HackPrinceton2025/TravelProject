import "./styles/globals.css";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-linear-to-br from-blue-50 via-white to-orange-50 min-h-screen text-gray-800">
        {children}
      </body>
    </html>
  );
}


