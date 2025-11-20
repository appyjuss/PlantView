import React from 'react';
import { Link } from 'react-router-dom';
import farmImage from '../../assets/farm.png';

const TopSection: React.FC = () => {
  return (
    <section className="flex flex-col-reverse lg:flex-row items-center gap-8 lg:gap-12">
      <div className="flex-1 min-w-0">
        <span className="inline-flex items-center gap-2 bg-emerald-100 text-emerald-700 px-4 py-1.5 rounded-full text-sm font-semibold">
          AI-Powered Plant Disease Detection
        </span>

        <h1 className="mt-6 text-3xl sm:text-4xl lg:text-5xl font-extrabold leading-tight text-slate-900">
          Protect Your Crops with
          <br />
          AI Technology — Plant View
        </h1>

        <p className="mt-4 text-lg text-slate-600 max-w-xl">
          Upload plant images and instantly detect potential diseases using our advanced CNN models. Empower your farming with AI technology for healthier crops and better yields.
        </p>

        <div className="mt-6 flex flex-wrap gap-4">
          <Link to="/dashboard" className="inline-flex items-center gap-2 bg-emerald-600 text-white px-5 py-3 rounded-md font-semibold shadow hover:bg-emerald-700">
            Try Disease Detection
          </Link>

          <Link to="#learn" className="inline-flex items-center gap-2 border border-emerald-600 text-emerald-600 px-5 py-3 rounded-md hover:bg-emerald-50">
            Learn More
          </Link>
        </div>

        <div className="mt-6 flex flex-wrap gap-6 text-sm text-slate-600">
          <span className="inline-flex items-center gap-2 font-medium">
            <span className="text-emerald-600">✓</span> Accurate AI Detection
          </span>
          <span className="inline-flex items-center gap-2 font-medium">
            <span className="text-emerald-600">🌿</span> CNN-Powered Analysis
          </span>
        </div>
      </div>

      <div className="w-full lg:w-1/2 max-w-lg rounded-xl overflow-hidden shadow-lg">
        <img src={farmImage} alt="Rows of plants in a greenhouse" className="w-full h-auto block" />
      </div>
    </section>
  );
};

export default TopSection;