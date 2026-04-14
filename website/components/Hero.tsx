"use client";

import { motion } from "framer-motion";

const HERO_PILLS = [
  "Indoor temperature and power draw",
  "Adaptive threshold window",
  "Savings surfaced early",
];

const HERO_METRICS = [
  { val: "10s", label: "Update Interval", note: "Sensor cadence", dot: "#84cc16" },
  { val: "4", label: "Fan Modes", note: "OFF to HIGH", dot: "#22d3ee" },
  { val: "3", label: "System Layers", note: "Edge, cloud, analytics", dot: "#f59e0b" },
  { val: "Live", label: "Sync State", note: "Weather-linked logic", dot: "#84cc16" },
];

const PREVIEW_TILES = [
  { label: "Current mode", value: "MEDIUM", hint: "Adaptive profile" },
  { label: "Power draw", value: "46W", hint: "Current reading" },
  { label: "Cloud sync", value: "10s", hint: "Steady cadence" },
];

const POWER_TRACE = [54, 82, 68, 94, 74, 58, 86, 66, 48];
const FLOW_NODES = ["Sensor", "Logic", "Cloud", "Insights"];

export default function Hero() {
  return (
    <section
      id="top"
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
        background: "#0f1115",
        paddingTop: "150px",
        paddingBottom: "110px",
      }}
    >
      <div className="ambient-orb ambient-orb-lime drift-slow" style={{ top: "-8%", left: "-4%" }} />
      <div className="ambient-orb ambient-orb-cyan drift-reverse" style={{ top: "14%", right: "-6%" }} />
      <div className="ambient-orb ambient-orb-amber drift-slow" style={{ bottom: "2%", left: "38%" }} />

      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.035,
          backgroundImage: "linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px)",
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      <div style={{ maxWidth: 1160, margin: "0 auto", padding: "0 24px", position: "relative", zIndex: 1 }}>
        <div className="hero-grid">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            style={{ textAlign: "left" }}
          >
            <div className="hero-status">
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#84cc16", display: "inline-block", animation: "pulse-dot 1.6s ease-in-out infinite" }} />
              ADAPTIVE CONTROL ONLINE
            </div>

            <h1
              style={{
                fontSize: "clamp(3.15rem, 6vw, 5.6rem)",
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 800,
                lineHeight: 0.96,
                letterSpacing: "-0.045em",
                color: "#ffffff",
                marginBottom: 18,
              }}
            >
              <span style={{ display: "block" }}>Weather-Adaptive</span>
              <span style={{ display: "block" }}>
                <span className="hero-kicker">IoT Energy</span> Monitor
              </span>
            </h1>

            <p
              style={{
                fontSize: "clamp(1rem, 1.8vw, 1.14rem)",
                color: "#7f8790",
                lineHeight: 1.75,
                maxWidth: 610,
                marginBottom: 34,
              }}
            >
              Track fan behavior, indoor conditions, and energy impact in one calmer interface built around the signals that matter first instead of repeating raw telemetry everywhere.
            </p>

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 28 }}>
              <a href="#dashboard" className="btn-primary">
                Open Dashboard
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </a>
              <a href="#how-it-works" className="btn-outline">
                See System Flow
              </a>
            </div>

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              {HERO_PILLS.map((pill) => (
                <span key={pill} className="hero-pill">
                  {pill}
                </span>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 36 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.12, ease: "easeOut" }}
            className="hero-console"
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, marginBottom: 24 }}>
              <div>
                <div className="section-label" style={{ marginBottom: 10 }}>Control Preview</div>
                <h2 style={{ fontSize: "1.55rem", color: "#ffffff" }}>Signals worth checking first</h2>
              </div>
              <div className="status-chip">ONLINE</div>
            </div>

            <div className="hero-console-grid">
              {PREVIEW_TILES.map((tile) => (
                <div key={tile.label} className="mini-kpi">
                  <div className="mini-kpi-label">{tile.label}</div>
                  <div className="mini-kpi-value">{tile.value}</div>
                  <div className="mini-kpi-hint">{tile.hint}</div>
                </div>
              ))}
            </div>

            <div className="signal-panel">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                <div>
                  <div className="signal-label">Power trace</div>
                  <div className="signal-subtle">Recent operating shifts</div>
                </div>
                <div className="signal-chip">Adaptive profile</div>
              </div>
              <div className="signal-bars">
                {POWER_TRACE.map((bar, index) => (
                  <motion.div
                    key={index}
                    className="signal-bar"
                    style={{ height: `${bar}px` }}
                    initial={{ opacity: 0, scaleY: 0.35 }}
                    animate={{ opacity: 1, scaleY: 1 }}
                    transition={{ duration: 0.45, delay: 0.08 * index, ease: "easeOut" }}
                  />
                ))}
              </div>
            </div>

            <div className="threshold-panel">
              <div className="threshold-card">
                <div className="threshold-label">Threshold window</div>
                <div className="threshold-value">Forecast-shaped control</div>
                <div className="threshold-note">MED and HIGH triggers shift with outdoor conditions.</div>
              </div>
              <div className="threshold-card">
                <div className="threshold-label">Savings posture</div>
                <div className="threshold-value">Compared with baseline</div>
                <div className="threshold-note">Energy impact stays visible next to system behavior.</div>
              </div>
            </div>

            <div className="path-row">
              {FLOW_NODES.map((node, index) => (
                <div key={node} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span className="path-node">{node}</span>
                  {index < FLOW_NODES.length - 1 ? <span className="path-arrow">+</span> : null}
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.2, ease: "easeOut" }}
          className="hero-metric-grid"
        >
          {HERO_METRICS.map((metric) => (
            <div key={metric.label} className="metric-card">
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <div style={{ width: 5, height: 5, borderRadius: "50%", background: metric.dot, opacity: 0.8, flexShrink: 0 }} />
                <div className="metric-card-label">{metric.label}</div>
              </div>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1.7rem", color: "#ffffff", lineHeight: 1.05 }}>{metric.val}</div>
              <div className="metric-card-note">{metric.note}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
