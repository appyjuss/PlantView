// import Hero from "../components/landing/Hero";
import FeatureSection from "../components/landing/FeaturesSection";
import How from "../components/landing/How";
import Footer from "../components/landing/Footer";
import Data from "@/components/landing/Data";
import TopSection from "@/components/landing/TopSection";


export default function Landing() {
  return (
    <main className="min-h-screen text-slate-900">
      <section
        id="TopSection"
        className="w-screen relative left-1/2 -translate-x-1/2 bg-white py-12"
      >
        <div className="container mx-auto px-6">
          <TopSection />
        </div>
      </section>
      <section
        id="FeatureSection"
        className="w-screen relative left-1/2 -translate-x-1/2 bg-white py-12"
      >
        <div className="container mx-auto px-6">
          <FeatureSection />
        </div>
      </section>
      <section
        id="learn"
        className="w-screen relative left-1/2 -translate-x-1/2 bg-gradient-to-b from-white to-gray-50 py-12"
      >
        <div className="container mx-auto px-6">
          <How />
        </div>
      </section>
      
      <section
        id="TopSection"
        className="w-screen relative left-1/2 -translate-x-1/2 bg-white py-12"
      >
        <div className="container mx-auto px-6">
          <Data />
        </div>
      </section>

      <Footer />
    </main>
  );
}