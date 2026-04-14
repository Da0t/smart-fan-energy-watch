"use client";

import { motion } from "framer-motion";

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || "http://localhost:8501";

export default function DashboardViewer() {
  return (
    <section id="dashboard" style={{ padding: "96px 24px", background: "#0f1115", borderTop: "1px solid #1c1c1c", position: "relative", overflow: "hidden" }}>
      <div className="ambient-orb ambient-orb-cyan drift-reverse" style={{ top: "12%", right: "-10%" }} />
      <div className="ambient-orb ambient-orb-lime drift-slow" style={{ bottom: "-10%", left: "-8%" }} />

      <div style={{ maxWidth: 1300, margin: "0 auto", position: "relative", zIndex: 1 }}>
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.25 }}
          transition={{ duration: 0.55, ease: "easeOut" }}
          style={{ textAlign: "center", marginBottom: 32 }}
        >
          <div className="section-label" style={{ marginBottom: 14 }}>Embedded Preview</div>
          <h2 style={{ fontSize: "clamp(1.8rem, 4vw, 2.8rem)", color: "#ffffff" }}>Open The Analytics Workspace</h2>
          <p style={{ color: "#666666", margin: "14px auto 0", fontSize: "1rem", maxWidth: 600, lineHeight: 1.75 }}>
            Use the inline frame for a quick check, or pop the Streamlit app into a full tab when you want filters and charts at full size.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.5, delay: 0.08, ease: "easeOut" }}
          style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16, flexWrap: "wrap", marginBottom: 18 }}
        >
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {["Streamlit on localhost", "Inline preview", "Full-screen ready"].map((label) => (
              <span key={label} className="hero-pill" style={{ color: "#8a8a8a" }}>
                {label}
              </span>
            ))}
          </div>
          <a href={DASHBOARD_URL} target="_blank" rel="noreferrer" className="btn-primary">
            Open Full Dashboard
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 26 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.55, delay: 0.12, ease: "easeOut" }}
          className="dashboard-shell"
        >
          <div
            style={{
              background: "#161616",
              borderBottom: "1px solid #1c1c1c",
              padding: "10px 16px",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <div style={{ display: "flex", gap: 6 }}>
              <div style={{ width: 11, height: 11, borderRadius: "50%", background: "#ef4444" }} />
              <div style={{ width: 11, height: 11, borderRadius: "50%", background: "#f59e0b" }} />
              <div style={{ width: 11, height: 11, borderRadius: "50%", background: "#84cc16" }} />
            </div>
            <div
              style={{
                flex: 1,
                background: "#0f1115",
                borderRadius: 6,
                padding: "5px 12px",
                fontSize: "0.74rem",
                color: "#555555",
                fontFamily: "monospace",
                border: "1px solid #1c1c1c",
              }}
            >
              {DASHBOARD_URL}
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.72rem", color: "#84cc16", fontWeight: 600, letterSpacing: "0.06em" }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#84cc16", display: "inline-block", animation: "pulse-dot 1.6s ease-in-out infinite" }} />
              LIVE
            </div>
          </div>

          <iframe
            src={DASHBOARD_URL}
            style={{ width: "100%", height: "85vh", minHeight: 700, border: "none", display: "block" }}
            title="Weather-Adaptive IoT Energy Monitor - Live Dashboard"
            allow="fullscreen"
          />
        </motion.div>

        <p className="dashboard-note">
          If the inline frame feels cramped or your browser blocks the embed, the full dashboard button above gives the best viewing experience.
        </p>
      </div>
    </section>
  );
}
