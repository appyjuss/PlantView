import React from 'react';
import './App.css'; 
import TopSection from './TopSection'; 
import FeaturesSection from './FeaturesSection'; 

function App() {
  return (
    <div className="App">
      <TopSection />
      
      <FeaturesSection />

      
      <div style={{ padding: '50px', textAlign: 'center', backgroundColor: '#f0f0f0' }}>
      </div>
    </div>
  );
}

export default App;