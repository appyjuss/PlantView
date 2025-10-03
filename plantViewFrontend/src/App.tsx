import React from 'react';
import './App.css'; 
import TopSection from './TopSection'; 

function App() {
  return (
    <div className="App">
      <TopSection />
      {}
      <div style={{ padding: '50px', textAlign: 'center' }}>
         <h2>[Content by Other Team Members Goes Here]</h2>
         <p>This is where the image upload form and detection results will be placed.</p>
      </div>
    </div>
  );
}

export default App;