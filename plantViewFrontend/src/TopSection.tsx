import React from 'react';
import './TopSection.css'; 
import farmImage from './assets/farm.png'; 

const TopSection: React.FC = () => {
  return (
    <section className="top-section-container">
      <div className="top-section-content">
        <span className="ts-badge">AI-Powered Plant Disease Detection</span>
        <h1>Protect Your Crops with <br />AI Technology</h1>
        <p className="ts-description">
          Upload plant images and instantly detect potential diseases using our advanced CNN models. 
          Empower your farming with AI technology for healthier crops and better yields.
        </p>
        <div className="ts-buttons">
          <button className="ts-btn-primary">Try Disease Detection</button>
          <button className="ts-btn-secondary">Learn More</button>
        </div>
        <div className="ts-features">
          <span>✅ Accurate AI Detection</span>
          <span>🌿 CNN-Powered Analysis</span>
        </div>
      </div>
      <div className="ts-image-container">
        <img src={farmImage} alt="Rows of plants in a greenhouse" className="ts-image" />
      </div>
    </section>
  );
};

export default TopSection;