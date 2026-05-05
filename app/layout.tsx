import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Sentinel-Poly | Polymarket Arbitrage Bot",
  description:
    "Real-time Polymarket CLOB scanner — liquidity arbitrage, news discrepancy detection, and Kelly-sized position management.",
  keywords: ["polymarket", "arbitrage", "prediction markets", "CLOB", "trading bot"],
  openGraph: {
    title: "Sentinel-Poly | Polymarket Arbitrage Bot",
    description: "AI-powered Polymarket edge detection and liquidity farming dashboard.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
