import React from 'react';
import './TopSection.css'; 
import farmImage from './assets/farm.png'; 

const TopSection: React.FC = () => {
  return (
    <section className="ts-container">
      <div className="ts-content">
        <span className="ts-badge">AI-Powered Plant Disease Detection</span>
        <h1>Protect Your Crops with <br />AI Technology- Plant View</h1>
        <p className="ts-description">
          Upload plant images and instantly detect potential diseases using our advanced CNN models. 
          Empower your farming with AI technology for healthier crops and better yields.
        </p>
        <div className="ts-buttons">
          <button className="ts-btn-primary">Try Disease Detection</button>
          <button className="ts-btn-secondary">Learn More</button>
        </div>
        <div className="ts-features">
          <span className="ts-feature-item">
            <span className="ts-icon-check">✓</span> Accurate AI Detection
          </span>
          <span className="ts-feature-item">
            <span className="ts-icon-leaf">🌿</span> CNN-Powered Analysis
          </span>
        </div>
      </div>
      <div className="ts-image-wrap">
        <img src={farmImage} alt="Rows of plants in a greenhouse" className="ts-image" />
      </div>
    </section>
  );
};

export default TopSection;