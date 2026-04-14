import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Weather-Adaptive IoT Energy Monitor",
  description: "Indoor fan telemetry, adaptive thresholds, and energy insight in one interface.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
