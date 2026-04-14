"use client";

import { motion } from "framer-motion";

const TECH = [
  { name: "ESP32", color: "#f59e0b" },
  { name: "C++", color: "#22d3ee" },
  { name: "Supabase", color: "#84cc16" },
  { name: "PostgreSQL", color: "#22d3ee" },
  { name: "Python", color: "#f59e0b" },
  { name: "Streamlit", color: "#ef4444" },
  { name: "Plotly", color: "#22d3ee" },
  { name: "Pandas", color: "#84cc16" },
  { name: "Open-Meteo", color: "#f59e0b" },
  { name: "DS18B20", color: "#888888" },
];

export default function TechStack() {
  return (
    <section style={{ padding: "72px 24px", maxWidth: 1100, margin: "0 auto", textAlign: "center" }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.35 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="section-label" style={{ marginBottom: 14 }}>Built With</div>
        <p style={{ color: "#666666", marginBottom: 28, fontSize: "0.98rem", lineHeight: 1.7 }}>
          A lean toolset for sensing, cloud sync, and analytics without extra visual noise in the stack or the interface.
        </p>
      </motion.div>
      <div className="stack-shell">
        {TECH.map((t, i) => (
          <motion.span
            key={t.name}
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.35, delay: i * 0.03, ease: "easeOut" }}
            className="tag-chip"
            style={{ fontFamily: "'Space Grotesk', sans-serif", cursor: "default" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = `${t.color}55`;
              e.currentTarget.style.color = t.color;
              e.currentTarget.style.background = "rgba(255,255,255,0.03)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "#2a2a2a";
              e.currentTarget.style.color = "#777777";
              e.currentTarget.style.background = "transparent";
            }}
          >
            {t.name}
          </motion.span>
        ))}
      </div>
    </section>
  );
}
