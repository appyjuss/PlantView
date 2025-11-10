import { UploadCloud, Image, FileText } from "lucide-react";

export default function How() {
	const steps = [
		{
			id: 1,
			title: "Upload Plant Image",
			desc: "Take a photo of your plant and upload it through our web interface.",
			Icon: UploadCloud,
		},
		{
			id: 2,
			title: "AI Analysis",
			desc: "Our models analyze the image to detect potential diseases and conditions.",
			Icon: Image,
		},
		{
			id: 3,
			title: "Get Results",
			desc: "Receive a detailed diagnosis with confidence levels and recommendations.",
			Icon: FileText,
		},
	];

	return (
		<section className="py-16">
			<div className="container mx-auto px-6">
				<div className="text-center">
					<h2 className="text-3xl font-extrabold text-slate-900 sm:text-4xl">
						<span>How PlantView Works</span>
					</h2>
					<p className="mt-4 text-teal-700 max-w-2xl mx-auto">
						Simple, fast, and accurate plant disease detection in just three easy
						steps.
					</p>
				</div>

        <div className="mt-10">
          <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 md:grid-cols-3">
            {steps.map((s) => (
              <article
                key={s.id}
                className="relative bg-white rounded-2xl p-8 shadow-[0_8px_24px_rgba(2,6,23,0.06)] hover:shadow-lg transition-shadow duration-150 flex flex-col items-center text-center"
              >
                {/* badge */}
                <div className="absolute top-4 right-4">
                  <div className="h-8 w-8 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-semibold ring-4 ring-white">
                    {s.id.toString().padStart(2, "0")}
                  </div>
                </div>

                {/* big icon */}
                <div className="mb-6">
                  <div className="h-20 w-20 rounded-full bg-gradient-to-tr from-emerald-400 to-emerald-600 flex items-center justify-center shadow-inner">
                    <s.Icon className="h-8 w-8 text-white" />
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-slate-900">{s.title}</h3>
                <p className="mt-3 text-sm text-slate-600 max-w-[20rem]">{s.desc}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
