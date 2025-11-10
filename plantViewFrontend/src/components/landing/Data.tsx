import { TrendingUp, Users, Leaf, Target } from "lucide-react";

export default function Data() {
  const items = [
    {
      id: 1,
      icon: TrendingUp,
      stat: "30%",
      statLabel: "Average yield improvement",
      title: "Improve Crop Yields",
      desc:
        "Early disease detection helps prevent crop losses and maximize your harvest potential.",
    },
    {
      id: 2,
      icon: Users,
      stat: "24/7",
      statLabel: "Available support",
      title: "Support Farmers",
      desc:
        "Empower farmers with accessible AI technology for better crop management decisions.",
    },
    {
      id: 3,
      icon: Leaf,
      stat: "50%",
      statLabel: "Reduction in pesticide use",
      title: "Sustainable Agriculture",
      desc:
        "Promote environmentally responsible farming through precision disease management.",
    },
    {
      id: 4,
      icon: Target,
      stat: "95%",
      statLabel: "Detection accuracy",
      title: "Precision Monitoring",
      desc:
        "Target specific plant issues with accurate AI-powered disease identification.",
    },
  ];

  return (
    <section className="py-16">
      <div className="container mx-auto px-6">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-slate-900 sm:text-4xl">
            Transforming Agriculture with AI
          </h2>
          <p className="mt-4 text-slate-600 max-w-3xl mx-auto">
            Discover how PlantView is helping farmers, researchers, and agricultural professionals make smarter decisions for healthier crops.
          </p>
        </div>

        <div className="mt-12">
          <div className="grid gap-12 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
            {items.map((it) => {
              const Icon = it.icon;
              return (
                <div
                  key={it.id}
                  className="bg-white rounded-2xl p-6 text-left shadow-[0_8px_24px_rgba(2,6,23,0.06)] flex flex-col"
                >
                  <div className="self-center mb-4 h-14 w-14 rounded-full bg-emerald-600 flex items-center justify-center">
                    <Icon className="h-6 w-6 text-white" aria-hidden="true" />
                  </div>

                  <div className="text-2xl font-extrabold text-emerald-600 self-center">{it.stat}</div>
                  <div className="text-xs text-slate-500 mt-1 self-center">{it.statLabel}</div>

                  <h3 className="mt-4 text-lg font-semibold text-slate-900">{it.title}</h3>
                  <p className="mt-3 text-sm text-slate-600">{it.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
