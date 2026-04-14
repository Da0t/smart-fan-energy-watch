const FOOTER_TAGS = ["ESP32", "Supabase", "Streamlit"];

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-brand">
        <div className="brand-mark">WA</div>
        <div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1rem", color: "#ffffff" }}>
            Weather-Adaptive Monitor
          </div>
          <div className="footer-copy">
            ESP32 telemetry to Supabase storage to Streamlit analytics.
          </div>
        </div>
      </div>

      <div className="footer-stack">
        {FOOTER_TAGS.map((tag) => (
          <span key={tag} className="tag-chip" style={{ cursor: "default" }}>
            {tag}
          </span>
        ))}
      </div>
    </footer>
  );
}
