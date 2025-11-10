import { UploadCloud, Cpu, BarChart2, Shield, Zap, Globe } from "lucide-react";

    const features = [
      {
        id: 1,
        Icon: UploadCloud,
        title: "Easy Image Upload",
        desc: "Simply upload plant images through our intuitive interface. Supports multiple image formats for maximum flexibility.",
      },
      {
        id: 2,
        Icon: Cpu,
        title: "CNN-Powered Detection",
        desc: "Advanced Convolutional Neural Networks trained on extensive plant disease datasets for accurate diagnosis.",
      },
      {
        id: 3,
        Icon: BarChart2,
        title: "Detailed Analysis",
        desc: "Get comprehensive reports with confidence levels and detailed insights about detected plant conditions.",
      },
      {
        id: 4,
        Icon: Shield,
        title: "Reliable Results",
        desc: "Our models are continuously trained and validated to provide consistent, trustworthy disease detection.",
      },
      {
        id: 5,
        Icon: Zap,
        title: "Instant Processing",
        desc: "Get results in seconds with our optimized machine learning pipeline and efficient processing algorithms.",
      },
      {
        id: 6,
        Icon: Globe,
        title: "Agricultural Impact",
        desc: "Supporting sustainable farming practices and helping reduce crop losses through early disease detection.",
      },
    ];

    export default function Features() {
      return (
        <section className="py-8">
          <div className="grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <div
                key={f.id}
                className="relative rounded-2xl bg-white p-8 shadow-[0_16px_40px_rgba(2,6,23,0.06)] overflow-hidden"
              >
                {/* subtle top gradient band */}
                <div className="absolute inset-x-0 top-0 h-20 rounded-t-2xl bg-gradient-to-b from-emerald-100/90 to-transparent -z-0" />

                {/* small icon in top-left (above gradient) */}
                <div className="absolute top-4 left-4 z-10">
                  <div className="h-12 w-12 rounded-lg bg-emerald-50/90 flex items-center justify-center shadow-sm ring-1 ring-emerald-100">
                    <f.Icon className="h-6 w-6 text-emerald-700" />
                  </div>
                </div>

                <div className="relative z-10 pt-2 pl-4">
                  <h3 className="text-lg font-semibold text-slate-900">{f.title}</h3>
                  <p className="mt-3 text-sm text-slate-600 max-w-xl">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      );
    }
