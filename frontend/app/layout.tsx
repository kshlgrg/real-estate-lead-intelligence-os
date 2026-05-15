import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lead Intelligence OS",
  description: "AI-powered real estate lead intelligence and routing platform"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
