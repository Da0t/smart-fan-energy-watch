"use client";

import { motion } from "framer-motion";
import type { CSSProperties } from "react";

const FEATURES = [
  { title: "Real-Time Telemetry",     desc: "ESP32 streams temperature, power draw, and fan mode to Supabase every 10 seconds with automatic reconnection.", accent: "#84cc16" },
  { title: "Weather-Adaptive Logic",  desc: "MED and HIGH thresholds shift dynamically with live outdoor temperature and daily peak via Open-Meteo.", accent: "#22d3ee" },
  { title: "Energy Savings Analysis", desc: "Time-weighted kWh integration compares adaptive usage against a constant baseline to quantify real savings.", accent: "#f59e0b" },
  { title: "Cost Impact Estimation",  desc: "Converts energy savings to dollar amounts at a configurable electricity rate in real time.", accent: "#84cc16" },
  { title: "Mode Distribution",       desc: "Breaks down how long the fan spent in each mode — OFF, LOW, MEDIUM, HIGH — over your chosen window.", accent: "#22d3ee" },
  { title: "Live Visualizations",     desc: "Temperature and power charts with mode-colored bands, threshold lines, and per-point hover tooltips.", accent: "#f59e0b" },
];

export default function Features() {
  return (
    <section id="features" style={{ padding: "96px 24px", background: "#0f1115", borderTop: "1px solid #1c1c1c", borderBottom: "1px solid #1c1c1c" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.35 }}
          transition={{ duration: 0.55, ease: "easeOut" }}
          style={{ textAlign: "center", marginBottom: 64 }}
        >
          <div className="section-label" style={{ marginBottom: 14 }}>What It Does</div>
          <h2 style={{ fontSize: "clamp(1.8rem, 4vw, 2.8rem)", color: "#ffffff" }}>Key Features</h2>
        </motion.div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 1, background: "#1e252f", borderRadius: 18, overflow: "hidden" }}>
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.4, delay: i * 0.05, ease: "easeOut" }}
              style={{
                background: "#0f1115",
                padding: "28px 26px",
                cursor: "default",
                position: "relative",
                overflow: "hidden",
              }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "#131922"; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "#0f1115"; }}
            >
              <div style={{ width: 4, height: 4, borderRadius: "50%", background: f.accent, marginBottom: 18, opacity: 0.8 }} />
              <h3 style={{ fontSize: "0.95rem", color: "#ffffff", marginBottom: 10, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600 }}>{f.title}</h3>
              <p style={{ fontSize: "0.84rem", color: "#666666", lineHeight: 1.75 }}>{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
