import React from 'react'
import { Link } from 'react-router-dom'
import leafLogo from '../assets/leaflogo.png'

export default function Footer() {
  return (
    <footer className="w-full bg-white border-t border-gray-200 mt-12 text-[#577b6b]">
      <div className="max-w-[1400px] mx-auto px-8 md:px-10 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-16">
          {/* Left column: logo, description, social icons */}
          <div>
            <Link to="/" className="flex items-center gap-3 mb-4">
              <img src={leafLogo} alt="PlantView" className="w-8 h-8 object-contain" />
              <span className="text-2xl font-semibold text-[#1f7a3e]">PlantView</span>
            </Link>

            <p className="text-gray-600 leading-relaxed mb-4">
              AI-powered plant disease detection using Convolutional Neural Networks. Helping farmers and researchers monitor crop health for better yields and sustainable agriculture.
            </p>

            <div className="flex items-center gap-4 mt-3 text-[#577b6b]">
              <a href="https://github.com/appyjuss/PlantView.git" aria-label="GitHub" className="hover:text-[#2f5f4c]" target="_blank" rel="noopener noreferrer">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 .5C5.73.5.75 5.48.75 11.75c0 4.93 3.19 9.11 7.6 10.59.56.1.77-.24.77-.54 0-.27-.01-1-.02-1.95-3.09.67-3.74-1.49-3.74-1.49-.51-1.29-1.25-1.63-1.25-1.63-1.02-.7.08-.69.08-.69 1.13.08 1.73 1.16 1.73 1.16 1.01 1.73 2.64 1.23 3.28.94.1-.74.39-1.23.71-1.51-2.47-.28-5.07-1.24-5.07-5.52 0-1.22.44-2.21 1.16-2.99-.12-.28-.5-1.42.11-2.96 0 0 .95-.31 3.12 1.15a10.78 10.78 0 012.84-.38c.96 0 1.92.13 2.84.38 2.17-1.46 3.12-1.15 3.12-1.15.61 1.54.23 2.68.11 2.96.72.78 1.16 1.77 1.16 2.99 0 4.29-2.61 5.23-5.09 5.51.39.33.73.98.73 1.98 0 1.43-.01 2.59-.01 2.95 0 .3.2.65.78.54C19.06 20.86 22.25 16.68 22.25 11.75 22.25 5.48 17.27.5 11 .5z"/>
                </svg>
              </a>

              <a href="mailto:info@plantview.example" aria-label="Email" className="hover:text-[#2f5f4c]">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                </svg>
              </a>

              <a href="#" aria-label="Website" className="hover:text-[#2f5f4c]">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 2c1.74 0 3.38.6 4.66 1.6L6.6 17.66A8 8 0 0112 4zm-6.6 3.34L17.34 17.66A8 8 0 015.4 7.34zM12 20a8 8 0 01-4.66-1.6L17.4 6.34A8 8 0 0112 20z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Middle column: Technology list */}
          <div>
            <h3 className="text-lg font-semibold text-[#1f7a3e] mb-4">Technology</h3>
            <ul className="space-y-3">
              <li><Link to="#" className="hover:text-[#2f5f4c]">CNN Models</Link></li>
              <li><Link to="#" className="hover:text-[#2f5f4c]">React Frontend</Link></li>
              <li><Link to="#" className="hover:text-[#2f5f4c]">Flask Backend</Link></li>
              <li><Link to="#" className="hover:text-[#2f5f4c]">Machine Learning</Link></li>
            </ul>
          </div>

          {/* Right column: Applications list */}
          <div>
            <h3 className="text-lg font-semibold text-[#1f7a3e] mb-4">Applications</h3>
            <ul className="space-y-3">
              <li><Link to="#" className="hover:text-[#2f5f4c]">Crop Monitoring</Link></li>
              <li><Link to="#" className="hover:text-[#2f5f4c]">Disease Detection</Link></li>
              <li><Link to="#" className="hover:text-[#2f5f4c]">Research Tools</Link></li>
              <li><Link to="#" className="hover:text-[#2f5f4c]">Smart Farming</Link></li>
            </ul>
          </div>
        </div>

        <hr className="my-8 border-gray-200" />

        <div className="text-center text-gray-600">
          <div className="mb-2">© {new Date().getFullYear()} PlantView — built with care.</div>
        </div>
      </div>
    </footer>
  )
}
