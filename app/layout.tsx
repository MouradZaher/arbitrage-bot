import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
    title: "Sentinel-Poly | Polymarket Arbitrage Bot",
    description: "Real-time Polymarket CLOB scanner for liquidity arbitrage and news discrepancy detection.",
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
