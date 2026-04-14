"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const NAV_ITEMS = [
  { label: "Overview", href: "#top" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Highlights", href: "#features" },
  { label: "Dashboard", href: "#dashboard" },
];

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", fn);
    return () => window.removeEventListener("scroll", fn);
  }, []);

  return (
    <motion.nav
      initial={{ y: -18, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.55, ease: "easeOut" }}
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      style={scrolled ? { background: "rgba(15,15,15,0.9)", backdropFilter: "blur(18px)", borderBottom: "1px solid #1c1c1c" } : {}}
    >
      <div style={{ maxWidth: 1160, margin: "0 auto", padding: "0 24px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 18, minHeight: 74 }}>
        <a href="#top" style={{ display: "flex", alignItems: "center", gap: 12, textDecoration: "none", minWidth: 0 }}>
          <div className="brand-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 2L3 13h7l-2 9 13-12h-8L13 2z" fill="#d9f99d"/>
            </svg>
          </div>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "0.98rem", color: "#ffffff", lineHeight: 1.1 }}>
              IoT Energy Monitor
            </div>
            <div style={{ fontSize: "0.72rem", color: "#666666", letterSpacing: "0.08em", textTransform: "uppercase", marginTop: 4 }}>
              Adaptive fan analytics
            </div>
          </div>
        </a>

        <div className="nav-links">
          {NAV_ITEMS.map((item) => (
            <a key={item.label} href={item.href} className="nav-link">
              {item.label}
            </a>
          ))}
        </div>

        <a href="#dashboard" className="btn-primary" style={{ padding: "10px 18px", fontSize: "0.84rem", whiteSpace: "nowrap" }}>
          Open Dashboard
        </a>
      </div>
    </motion.nav>
  );
}
