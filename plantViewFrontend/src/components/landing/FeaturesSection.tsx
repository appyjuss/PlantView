import React from 'react';
import './FeaturesSection.css';

const FeaturesSection: React.FC = () => {
  return (
    <section id="features" className="fs-container">
      <div className="fs-header">
        <h2>Powerful Features for <span>Smart Farming</span></h2>
        <p className="fs-description">
          Our AI-powered platform combines cutting-edge technology with practical 
          agricultural solutions to help you monitor and protect your crops.
        </p>
      </div>
    </section>
  );
};

export default FeaturesSection;