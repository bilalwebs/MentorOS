import type { Metadata } from "next";
import { Providers } from "@/lib/providers";
import { ErrorBoundary } from "@/components/common/error-boundary";
import "./globals.css";

export const metadata: Metadata = {
  title: "MentorOS — AI Student Growth Platform",
  description: "An AI mentor with persistent memory of your learning journey.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <ErrorBoundary>
          <Providers>{children}</Providers>
        </ErrorBoundary>
      </body>
    </html>
  );
}
