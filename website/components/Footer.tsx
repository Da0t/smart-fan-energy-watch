export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-brand">
        <div className="brand-mark">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L3 13h7l-2 9 13-12h-8L13 2z" fill="#d9f99d"/>
          </svg>
        </div>
        <div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1rem", color: "#ffffff" }}>
            Weather-Adaptive Monitor
          </div>
          <div className="footer-copy">
            ESP32 telemetry to Supabase storage to Streamlit analytics.
          </div>
        </div>
      </div>
    </footer>
  );
}
