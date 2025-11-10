// import Hero from "../components/landing/Hero";
import Features from "../components/landing/Features";
import How from "../components/landing/How";
import Footer from "../components/landing/Footer";
import Data from "@/components/landing/Data";


export default function Landing() {
  return (
    <main className="min-h-screen   text-slate-900">
      <div className="container mx-auto px-6 py-12 lg:flex lg:items-start lg:gap-12">
        {/* <Hero /> */}
        <div className="mt-8 lg:mt-0">
          
        </div>
      </div>
      <section id="features" className="container mx-auto py-12">
        <Features />
      </section>
      {/* full-bleed gradient that escapes the parent container*/}
      <section
        id="how"
        className="w-screen relative left-1/2 -translate-x-1/2 bg-gradient-to-b from-white to-gray-50 py-12"
      >
        <div className="container mx-auto px-6">
          <How />
        </div>
      </section>
      <section id="data" className="container mx-auto py-12">
        <Data />
      </section>

      <Footer />
    </main>
  );
}