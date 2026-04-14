import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import Features from "@/components/Features";
import TechStack from "@/components/TechStack";
import DashboardViewer from "@/components/DashboardViewer";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main style={{ minHeight: "100vh" }}>
      <Nav />
      <Hero />
      <HowItWorks />
      <Features />
      <TechStack />
      <DashboardViewer />
      <Footer />
    </main>
  );
}
