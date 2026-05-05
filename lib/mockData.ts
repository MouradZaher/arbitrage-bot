/**
 * Mock data utilities
 */
export type Signal = "OPPORTUNITY" | "VEGAS_GAP" | "CIRCUIT_BREAKER" | "PASSIVE";
export interface Opportunity {
    id: string; timestamp: string; question: string; token_id: string; mid: number; sentiment: number; delta: number; edge: number; kelly_usdc: number; signal: Signal; spread_pct: number; bid: number; ask: number; projected_roi: number; category: string;
}
export interface BotStatus {
    capital: number; daily_pnl: number; drawdown_pct: number; kill_limit: number; kill_active: boolean; trades_today: number; scan_count: number; last_scan: string; status: "RUNNING" | "PAUSED" | "KILLED";
}
const QUESTIONS = ["Will Donald Trump be impeached before 2027?", "Will the Fed cut rates in June 2026?"];
const CATEGORIES = ["Politics", "Finance"];
function rand(min: number, max: number, dp = 3) { return parseFloat((Math.random() * (max - min) + min).toFixed(dp)); }
export function generateOpportunities(n = 20): Opportunity[] {
    return Array.from({ length: n }, (_, i) => ({
          id: `opp-${i}`, timestamp: new Date().toISOString(), question: QUESTIONS[i % QUESTIONS.length], token_id: "0x123", mid: 0.5, sentiment: 0.6, delta: 0.1, edge: 0.1, kelly_usdc: 50, signal: "OPPORTUNITY", spread_pct: 0.5, bid: 0.49, ask: 0.51, projected_roi: 2.5, category: CATEGORIES[i % CATEGORIES.length]
    }));
}
export function generateBotStatus(): BotStatus { return { capital: 2850, daily_pnl: 100, drawdown_pct: 0, kill_limit: 5, kill_active: false, trades_today: 5, scan_count: 10, last_scan: new Date().toISOString(), status: "RUNNING" }; }
export function generatePnlHistory(points = 48) { return Array.from({ length: points }, (_, i) => ({ time: "12:00", pnl: 5, cumulative: 100 })); }
