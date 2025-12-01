import React from 'react'
import { Link } from 'react-router-dom'
import leafLogo from '../assets/leaflogo.png'

export default function Header() {
  return (
    <header className="w-full bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="w-full max-w-[1400px] mx-auto px-10 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 font-bold text-2xl text-[#1f7a3e]">
          <img src={leafLogo} alt="PlantView" className="w-8 h-8 object-contain" />
          <span>PlantView</span>
        </Link>

        <nav className="hidden md:flex items-center gap-10" aria-label="Main navigation">
          <Link to="/" className="text-lg font-medium text-[#577b6b] hover:text-[#2f5f4c]">Home</Link>
          <Link
            to="/#features"
            onClick={(e) => {
              // If already on the landing page, prevent navigation and smooth-scroll to the section
              if (window.location.pathname === '/') {
                e.preventDefault();
                const el = document.getElementById('features');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }
            }}
            className="text-lg font-medium text-[#577b6b] hover:text-[#2f5f4c]"
          >
            Features
          </Link>
          <Link to="/dashboard" className="text-lg font-medium text-[#577b6b] hover:text-[#2f5f4c]">Dashboard</Link>
          <Link
            to="/#data"
            onClick={(e) => {
              if (window.location.pathname === '/') {
                e.preventDefault();
                const el = document.getElementById('data');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }
            }}
            className="text-lg font-medium text-[#577b6b] hover:text-[#2f5f4c]"
          >
            About
          </Link>
        </nav>

        <div className="ml-4">
          <Link to="/upload" className="inline-block bg-[#27ae60] text-white px-5 py-2 rounded-full shadow-md text-lg font-semibold hover:bg-[#229954] transform hover:-translate-y-0.5 transition">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  )
}
