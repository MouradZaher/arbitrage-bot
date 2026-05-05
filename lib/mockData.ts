/**
 * Mock data utilities — generates realistic-looking Polymarket scan data
 * for dashboard demo / simulation review.
 */

export type Signal = "OPPORTUNITY" | "VEGAS_GAP" | "CIRCUIT_BREAKER" | "PASSIVE";

export interface Opportunity {
  id: string;
  timestamp: string;
  question: string;
  token_id: string;
  mid: number;
  sentiment: number;
  delta: number;
  edge: number;
  kelly_usdc: number;
  signal: Signal;
  spread_pct: number;
  bid: number;
  ask: number;
  projected_roi: number;
  category: string;
}

export interface BotStatus {
  capital: number;
  daily_pnl: number;
  drawdown_pct: number;
  kill_limit: number;
  kill_active: boolean;
  trades_today: number;
  scan_count: number;
  last_scan: string;
  status: "RUNNING" | "PAUSED" | "KILLED";
}

const QUESTIONS = [
  "Will Donald Trump be impeached before 2027?",
  "Will the Fed cut rates in June 2026?",
  "Will Bitcoin exceed $120k by end of 2026?",
  "Will France win Euro 2028?",
  "Will Elon Musk remain Tesla CEO through Q3 2026?",
  "Will the US enter a recession in 2026?",
  "Will OpenAI release GPT-5 before July 2026?",
  "Will Ukraine and Russia sign a ceasefire in 2026?",
  "Will Apple acquire Netflix by end of 2026?",
  "Will Nvidia surpass $5T market cap in 2026?",
  "Will the S&P 500 end 2026 above 6000?",
  "Will there be a US government shutdown in Q2 2026?",
  "Will Kamala Harris run in 2028?",
  "Will Solana flip Ethereum by TVL in 2026?",
  "Will SpaceX reach orbit with Starship in 2026?",
  "Will inflation drop below 2% in the US by Q4 2026?",
  "Will the UK rejoin the EU single market?",
  "Will Polymarket exceed $5B monthly volume in 2026?",
  "Will China invade Taiwan before 2027?",
  "Will a new COVID variant cause lockdowns in 2026?",
];

const CATEGORIES = ["Politics", "Finance", "Crypto", "Sports", "Tech", "Macro"];

function rand(min: number, max: number, dp = 3) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(dp));
}

function randomSignal(): Signal {
  const r = Math.random();
  if (r < 0.35) return "OPPORTUNITY";
  if (r < 0.50) return "VEGAS_GAP";
  if (r < 0.60) return "CIRCUIT_BREAKER";
  return "PASSIVE";
}

export function generateOpportunities(n = 20): Opportunity[] {
  return Array.from({ length: n }, (_, i) => {
    const mid = rand(0.05, 0.95);
    const sentiment = rand(0.05, 0.95);
    const delta = Math.abs(mid - sentiment);
    const signal = delta > 0.10 ? (Math.random() > 0.4 ? "OPPORTUNITY" : "VEGAS_GAP") : randomSignal();
    const edge = signal === "OPPORTUNITY" || signal === "VEGAS_GAP" ? delta : rand(0, 0.05);
    const odds = mid > 0 ? 1 / mid - 1 : 1;
    const kelly_usdc = signal === "OPPORTUNITY" ? rand(5, 57) : 0;
    const spread_pct = signal === "CIRCUIT_BREAKER" ? rand(2.1, 5) : rand(0.1, 1.8);
    const bid = parseFloat((mid - spread_pct / 200).toFixed(4));
    const ask = parseFloat((mid + spread_pct / 200).toFixed(4));

    return {
      id: `opp-${i}-${Date.now()}`,
      timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      question: QUESTIONS[i % QUESTIONS.length],
      token_id: `0x${Math.random().toString(16).slice(2, 18)}`,
      mid,
      sentiment,
      delta,
      edge,
      kelly_usdc,
      signal,
      spread_pct,
      bid,
      ask,
      projected_roi: parseFloat((edge * kelly_usdc / 2850 * 100).toFixed(3)),
      category: CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)],
    };
  });
}

export function generateBotStatus(): BotStatus {
  const daily_pnl = rand(-80, 120, 2);
  const capital = 2850;
  return {
    capital,
    daily_pnl,
    drawdown_pct: daily_pnl < 0 ? parseFloat((Math.abs(daily_pnl) / capital * 100).toFixed(2)) : 0,
    kill_limit: 5,
    kill_active: daily_pnl < -142.5,
    trades_today: Math.floor(Math.random() * 18),
    scan_count: Math.floor(Math.random() * 120) + 1,
    last_scan: new Date().toISOString(),
    status: daily_pnl < -142.5 ? "KILLED" : "RUNNING",
  };
}

export function generatePnlHistory(points = 48): { time: string; pnl: number; cumulative: number }[] {
  let cum = 0;
  return Array.from({ length: points }, (_, i) => {
    const pnl = rand(-8, 12, 2);
    cum += pnl;
    return {
      time: new Date(Date.now() - (points - i) * 30 * 60 * 1000).toLocaleTimeString("en-US", {
        hour: "2-digit", minute: "2-digit",
      }),
      pnl: parseFloat(pnl.toFixed(2)),
      cumulative: parseFloat(cum.toFixed(2)),
    };
  });
}
