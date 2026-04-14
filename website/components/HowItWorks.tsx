"use client";

import { motion } from "framer-motion";

const STEPS = [
  {
    num: "01",
    title: "ESP32 Edge Device",
    color: "#f59e0b",
    desc: "The sensor captures room conditions on a short interval and hands those readings to weather-aware fan logic at the edge.",
    tags: ["C++", "DS18B20", "Open-Meteo", "Wi-Fi"],
  },
  {
    num: "02",
    title: "Supabase Cloud Layer",
    color: "#22d3ee",
    desc: "Each reading is stored in a clean cloud stream so the dashboard can query history without talking to the device directly.",
    tags: ["PostgreSQL", "REST API", "Streaming", "Cloud"],
  },
  {
    num: "03",
    title: "Streamlit Analytics",
    color: "#84cc16",
    desc: "The analytics view turns that feed into mode history, baseline comparisons, and cost context that are easier to explain at a glance.",
    tags: ["Python", "Streamlit", "Plotly", "Pandas"],
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" style={{ padding: "96px 24px", maxWidth: 1100, margin: "0 auto" }}>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.35 }}
        transition={{ duration: 0.55, ease: "easeOut" }}
        style={{ textAlign: "center", marginBottom: 64 }}
      >
        <div className="section-label" style={{ marginBottom: 14 }}>System Flow</div>
        <h2 style={{ fontSize: "clamp(1.8rem, 4vw, 2.8rem)", color: "#ffffff" }}>How It Works</h2>
        <p style={{ color: "#666666", margin: "14px auto 0", fontSize: "1rem", maxWidth: 560, lineHeight: 1.75 }}>
          One measurement moves through three stages: capture at the edge, sync in the cloud, and analysis in the browser.
        </p>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 1, background: "#1c1c1c", borderRadius: 18, overflow: "hidden" }}>
        {STEPS.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 28 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.25 }}
            transition={{ duration: 0.45, delay: i * 0.08, ease: "easeOut" }}
            className="info-card"
            style={{ padding: "36px 32px", position: "relative", minHeight: 320 }}
          >
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "4rem", fontWeight: 800, color: "#ffffff", opacity: 0.04, position: "absolute", top: 12, right: 24, lineHeight: 1 }}>{step.num}</div>
            <div style={{ width: 4, height: 4, borderRadius: "50%", background: step.color, marginBottom: 20, opacity: 0.8 }} />
            <h3 style={{ fontSize: "1.1rem", color: "#ffffff", marginBottom: 12, fontFamily: "'Space Grotesk', sans-serif" }}>{step.title}</h3>
            <p style={{ fontSize: "0.87rem", color: "#666666", lineHeight: 1.75, marginBottom: 24 }}>{step.desc}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {step.tags.map((tag) => (
                <span key={tag} className="tag-chip">
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 10, marginTop: 28, opacity: 0.32, flexWrap: "wrap" }}>
        <span style={{ fontSize: "0.72rem", color: "#888888", letterSpacing: "0.1em" }}>ESP32</span>
        <svg width="60" height="8" viewBox="0 0 60 8"><path d="M0 4h52M49 1l3 3-3 3" stroke="#888" strokeWidth="1.2" fill="none" strokeLinecap="round" /></svg>
        <span style={{ fontSize: "0.72rem", color: "#888888", letterSpacing: "0.1em" }}>SUPABASE</span>
        <svg width="60" height="8" viewBox="0 0 60 8"><path d="M0 4h52M49 1l3 3-3 3" stroke="#888" strokeWidth="1.2" fill="none" strokeLinecap="round" /></svg>
        <span style={{ fontSize: "0.72rem", color: "#888888", letterSpacing: "0.1em" }}>STREAMLIT</span>
      </div>
    </section>
  );
}
