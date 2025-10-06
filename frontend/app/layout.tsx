import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Robotics SOTA Dashboard",
  description: "Interactive robotics research trends without the map visualization."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </div>
      </body>
    </html>
  );
}
