"use client";

import { useEffect, useState, useCallback } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Cell
} from "recharts";
import {
  generateOpportunities, generateBotStatus, generatePnlHistory,
  type Opportunity, type BotStatus
} from "@/lib/mockData";
import styles from "./page.module.css";

// ── Signal colours ─────────────────────────────────────────────
const SIGNAL_CONFIG: Record<string, { badge: string; label: string; emoji: string }> = {
  OPPORTUNITY:     { badge: "badge-green",  label: "Opportunity",     emoji: "🟢" },
  VEGAS_GAP:       { badge: "badge-purple", label: "Vegas Gap",       emoji: "🎰" },
  CIRCUIT_BREAKER: { badge: "badge-red",    label: "Circuit Breaker", emoji: "⚡" },
  PASSIVE:         { badge: "badge-cyan",   label: "Passive MM",      emoji: "📊" },
};

// ── Stat Card ──────────────────────────────────────────────────
function StatCard({
  label, value, sub, accent, pulse, icon,
}: {
  label: string; value: string | number; sub?: string;
  accent?: "green" | "red" | "amber" | "purple" | "cyan"; pulse?: boolean; icon: string;
}) {
  const colourMap = { green: "#00ff88", red: "#ff4757", amber: "#ffa502", purple: "#a855f7", cyan: "#00d4ff" };
  const colour = accent ? colourMap[accent] : "#00ff88";

  return (
    <div className={`card ${styles.statCard}`}>
      <div className={styles.statIcon} style={{ color: colour }}>{icon}</div>
      <div className={styles.statLabel}>{label}</div>
      <div
        className={`${styles.statValue} ${accent === "green" ? "glow-green" : accent === "red" ? "glow-red" : ""}`}
        style={{ color: colour }}
      >
        {value}
        {pulse && <span className={`${styles.dot} pulse`} style={{ background: colour }} />}
      </div>
      {sub && <div className={styles.statSub}>{sub}</div>}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────
export default function Dashboard() {
  const [opps, setOpps]       = useState<Opportunity[]>([]);
  const [status, setStatus]   = useState<BotStatus | null>(null);
  const [pnlData, setPnlData] = useState<ReturnType<typeof generatePnlHistory>>([]);
  const [filter, setFilter]   = useState<string>("ALL");
  const [tick, setTick]       = useState(0);
  const [scanning, setScanning] = useState(false);

  const refresh = useCallback(() => {
    setScanning(true);
    setTimeout(() => {
      setOpps(generateOpportunities(20));
      setStatus(generateBotStatus());
      setPnlData(generatePnlHistory(48));
      setScanning(false);
      setTick(t => t + 1);
    }, 600);
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Auto-refresh every 30 s
  useEffect(() => {
    const id = setInterval(refresh, 30_000);
    return () => clearInterval(id);
  }, [refresh]);

  const signals = ["ALL", "OPPORTUNITY", "VEGAS_GAP", "CIRCUIT_BREAKER", "PASSIVE"];
  const filtered = filter === "ALL" ? opps : opps.filter(o => o.signal === filter);
  const activeOpps = opps.filter(o => o.signal === "OPPORTUNITY" || o.signal === "VEGAS_GAP");

  if (!status) return (
    <div className={styles.loading}>
      <div className={styles.spinner} />
      <p>Connecting to Polymarket CLOB…</p>
    </div>
  );

  return (
    <div className={styles.page}>
      {/* ── Header ─────────────────────────────────────────── */}
      <header className={styles.header}>
        <div className="container">
          <div className={styles.headerInner}>
            <div className={styles.logo}>
              <span className={styles.logoIcon}>⚡</span>
              <div>
                <h1 className={`${styles.logoTitle} gradient-text`}>Sentinel-Poly</h1>
                <p className={styles.logoSub}>Polymarket Arbitrage &amp; Liquidity Bot</p>
              </div>
            </div>
            <div className={styles.headerRight}>
              <div className={styles.statusPill} data-status={status.status}>
                <span className={styles.statusDot} />
                {status.status}
              </div>
              <button
                className="btn btn-primary"
                onClick={refresh}
                disabled={scanning}
                id="btn-refresh"
              >
                {scanning ? "⟳ Scanning…" : "↺ Refresh"}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container">

        {/* ── Kill Switch Banner ─────────────────────────── */}
        {status.kill_active && (
          <div className={`${styles.killBanner} fade-in`}>
            🚨 <strong>KILL SWITCH ACTIVE</strong> — Daily drawdown exceeded {status.kill_limit}%.
            All orders cancelled. Manual review required.
          </div>
        )}

        {/* ── Stat Row ──────────────────────────────────── */}
        <section className={styles.statsGrid}>
          <StatCard
            icon="💰" label="Total Capital" value={`$${status.capital.toLocaleString()}`}
            sub="USDC.e on Polygon" accent="green"
          />
          <StatCard
            icon="📈" label="Daily P&amp;L"
            value={`${status.daily_pnl >= 0 ? "+" : ""}$${status.daily_pnl.toFixed(2)}`}
            sub={`${Math.abs(status.daily_pnl / status.capital * 100).toFixed(2)}% return`}
            accent={status.daily_pnl >= 0 ? "green" : "red"}
            pulse={status.status === "RUNNING"}
          />
          <StatCard
            icon="🛡️" label="Drawdown"
            value={`${status.drawdown_pct.toFixed(2)}%`}
            sub={`Kill at ${status.kill_limit}%`}
            accent={status.drawdown_pct > 3 ? "red" : "amber"}
          />
          <StatCard
            icon="🎯" label="Opportunities"
            value={activeOpps.length}
            sub={`of ${opps.length} markets scanned`}
            accent="purple"
          />
          <StatCard
            icon="🔄" label="Trades Today"
            value={status.trades_today}
            sub={`Scan #${status.scan_count}`}
            accent="cyan" pulse
          />
          <StatCard
            icon="⚙️" label="Max / Trade"
            value={`$${(status.capital * 0.02).toFixed(2)}`}
            sub="Half-Kelly capped at 2%"
            accent="green"
          />
        </section>

        {/* ── Charts ────────────────────────────────────── */}
        <section className={styles.chartsGrid}>
          {/* Cumulative P&L */}
          <div className="card">
            <div className={styles.chartHeader}>
              <h2 className={styles.chartTitle}>Cumulative P&amp;L</h2>
              <span className="badge badge-green">48h window</span>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={pnlData}>
                <defs>
                  <linearGradient id="pnlGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#00ff88" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="time" tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} interval={7} />
                <YAxis tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                <Tooltip
                  contentStyle={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`$${v}`, "Cumulative P&L"]}
                />
                <Area type="monotone" dataKey="cumulative" stroke="#00ff88" strokeWidth={2} fill="url(#pnlGrad)" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Per-scan P&L bars */}
          <div className="card">
            <div className={styles.chartHeader}>
              <h2 className={styles.chartTitle}>Per-Scan P&amp;L</h2>
              <span className="badge badge-cyan">30 min intervals</span>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={pnlData.slice(-24)}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="time" tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} interval={5} />
                <YAxis tick={{ fill: "#484f58", fontSize: 10 }} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                <Tooltip
                  contentStyle={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`$${v}`, "P&L"]}
                />
                <Bar dataKey="pnl" radius={[3, 3, 0, 0]}>
                  {pnlData.slice(-24).map((entry, i) => (
                    <Cell key={i} fill={entry.pnl >= 0 ? "#00ff88" : "#ff4757"} fillOpacity={0.8} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* ── Opportunities Table ────────────────────────── */}
        <section className={`card ${styles.tableSection}`}>
          <div className={styles.tableHeader}>
            <div>
              <h2 className={styles.chartTitle}>Market Scan Results</h2>
              <p className={styles.tableSubtitle}>
                Scan #{tick} · {new Date(status.last_scan).toLocaleTimeString()} ·{" "}
                {activeOpps.length} active signals
              </p>
            </div>
            <div className={styles.filterRow}>
              {signals.map(s => (
                <button
                  key={s}
                  className={`${styles.filterBtn} ${filter === s ? styles.filterActive : ""}`}
                  onClick={() => setFilter(s)}
                  id={`filter-${s.toLowerCase()}`}
                >
                  {s === "ALL" ? `All (${opps.length})` : s.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.tableWrapper}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Signal</th>
                  <th>Market Question</th>
                  <th>Category</th>
                  <th>Mid Price</th>
                  <th>Sentiment</th>
                  <th>Δ Divergence</th>
                  <th>Spread</th>
                  <th>Kelly Size</th>
                  <th>Proj. ROI</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(opp => {
                  const cfg = SIGNAL_CONFIG[opp.signal];
                  return (
                    <tr key={opp.id} className={styles.tableRow}>
                      <td>
                        <span className={`badge ${cfg.badge}`}>
                          {cfg.emoji} {cfg.label}
                        </span>
                      </td>
                      <td className={styles.questionCell}>
                        <span className={styles.questionText}>{opp.question}</span>
                        <span className={`mono ${styles.tokenId}`}>{opp.token_id.slice(0, 10)}…</span>
                      </td>
                      <td>
                        <span className="badge badge-cyan">{opp.category}</span>
                      </td>
                      <td className="mono">{opp.mid.toFixed(3)}</td>
                      <td className="mono">{opp.sentiment.toFixed(3)}</td>
                      <td>
                        <div className={styles.deltaCell}>
                          <span
                            className="mono"
                            style={{ color: opp.delta > 0.1 ? "#00ff88" : opp.delta > 0.05 ? "#ffa502" : "#7d8590" }}
                          >
                            {(opp.delta * 100).toFixed(1)}%
                          </span>
                          <div className="progress-bar" style={{ width: 60, marginTop: 4 }}>
                            <div
                              className="progress-fill"
                              style={{
                                width: `${Math.min(opp.delta * 500, 100)}%`,
                                background: opp.delta > 0.1 ? "#00ff88" : "#ffa502",
                              }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="mono">{opp.spread_pct.toFixed(2)}%</td>
                      <td className="mono">
                        {opp.kelly_usdc > 0 ? (
                          <span style={{ color: "#00ff88" }}>${opp.kelly_usdc.toFixed(2)}</span>
                        ) : (
                          <span style={{ color: "#484f58" }}>—</span>
                        )}
                      </td>
                      <td className="mono">
                        {opp.projected_roi > 0 ? (
                          <span style={{ color: "#00ff88" }}>+{opp.projected_roi.toFixed(3)}%</span>
                        ) : (
                          <span style={{ color: "#484f58" }}>—</span>
                        )}
                      </td>
                      <td className={styles.timeCell}>
                        {new Date(opp.timestamp).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        {/* ── Risk Panel ─────────────────────────────────── */}
        <section className={styles.riskGrid}>
          <div className="card">
            <h2 className={styles.chartTitle}>Sentinel Protocol</h2>
            <div className={styles.riskRow}>
              <span>Daily Drawdown</span>
              <div style={{ flex: 1, margin: "0 12px" }}>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.min(status.drawdown_pct / status.kill_limit * 100, 100)}%`,
                      background: status.drawdown_pct > 3 ? "#ff4757" : status.drawdown_pct > 1.5 ? "#ffa502" : "#00ff88",
                    }}
                  />
                </div>
              </div>
              <span className="mono">{status.drawdown_pct.toFixed(2)}% / {status.kill_limit}%</span>
            </div>
            <div className={styles.riskRow}>
              <span>Capital Deployed</span>
              <div style={{ flex: 1, margin: "0 12px" }}>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${status.trades_today * 2}%`, background: "#a855f7" }} />
                </div>
              </div>
              <span className="mono">{(status.trades_today * 2).toFixed(0)}%</span>
            </div>
            <div className={styles.riskItems}>
              <div className={styles.riskItem}>
                <span className={`badge ${status.kill_active ? "badge-red" : "badge-green"}`}>
                  {status.kill_active ? "⚠ Kill Active" : "✓ Kill Idle"}
                </span>
              </div>
              <div className={styles.riskItem}>
                <span className="badge badge-cyan">Half-Kelly</span>
              </div>
              <div className={styles.riskItem}>
                <span className="badge badge-amber">Limit Orders Only</span>
              </div>
              <div className={styles.riskItem}>
                <span className="badge badge-purple">2% Spread CB</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className={styles.chartTitle}>Signal Distribution</h2>
            <div className={styles.signalDist}>
              {Object.entries(SIGNAL_CONFIG).map(([key, cfg]) => {
                const count = opps.filter(o => o.signal === key).length;
                const pct   = opps.length > 0 ? (count / opps.length * 100) : 0;
                return (
                  <div key={key} className={styles.distRow}>
                    <span className={`badge ${cfg.badge}`}>{cfg.emoji} {cfg.label}</span>
                    <div style={{ flex: 1, margin: "0 12px" }}>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{
                          width: `${pct}%`,
                          background: key === "OPPORTUNITY" ? "#00ff88"
                            : key === "VEGAS_GAP" ? "#a855f7"
                            : key === "CIRCUIT_BREAKER" ? "#ff4757"
                            : "#00d4ff",
                        }} />
                      </div>
                    </div>
                    <span className="mono" style={{ minWidth: 28 }}>{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* ── Footer ─────────────────────────────────────── */}
        <footer className={styles.footer}>
          <p>
            Sentinel-Poly · Polygon CLOB ·{" "}
            <a
              href="https://docs.polymarket.com"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.footerLink}
            >
              Polymarket Docs
            </a>
            {" "}·{" "}
            <span style={{ color: "#484f58" }}>
              ⚠ Not financial advice. Always review before live execution.
            </span>
          </p>
        </footer>

      </main>
    </div>
  );
}
