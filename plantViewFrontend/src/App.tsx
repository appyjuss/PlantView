import React, { useState, useCallback } from 'react';
import './App.css';

// Define the API URL. This is the missing Flask server address.
// We will set a placeholder state for now.
const API_URL = 'http://127.0.0.1:5000/predict';

interface Prediction {
  class: string;
  confidence: number;
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null;
    setSelectedFile(file);
    setPrediction(null); // Reset prediction on new file upload
    setError(null); // Clear previous errors

    if (file) {
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      setPreviewUrl(null);
    }
  };

  const handlePredict = useCallback(async () => {
    if (!selectedFile) {
      setError("Please select an image file first.");
      return;
    }

    setLoading(true);
    setError(null);

    // ***************************************************************
    // WARNING: This section WILL FAIL because the backend server is not running.
    // The previous error you saw (ECONNREFUSED) will likely appear here.
    // You are seeing this code to restore the UI.
    // ***************************************************************
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPrediction({
        class: data.class || 'Unknown Class',
        confidence: data.confidence || 0.0,
      });

    } catch (err) {
      // Set a prediction result even on failure so the UI still displays the prediction box
      setPrediction({
        class: "Backend Not Running",
        confidence: 0.0,
      });
      setError("Error: Could not connect to the backend server (Flask). Please start the backend in a separate terminal.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedFile]);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>PlantView 🌱</h1>
        <p>Upload a plant image to detect potential diseases using AI.</p>
      </header>
      
      <main className="main-content">
        <div className="file-upload-section">
          <input 
            type="file" 
            accept="image/*" 
            onChange={handleFileChange} 
            className="file-input"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="file-upload-label">
            {selectedFile ? selectedFile.name : "Choose Image"}
          </label>
          <button 
            onClick={handlePredict} 
            disabled={!selectedFile || loading}
            className="predict-button"
          >
            {loading ? 'Predicting...' : 'Detect Disease'}
          </button>
        </div>

        {error && <p className="error-message">{error}</p>}
        
        <div className="results-container">
          <div className="image-preview-card">
            <h2>Image Preview</h2>
            {previewUrl ? (
              <img src={previewUrl} alt="Preview" className="image-preview" />
            ) : (
              <div className="placeholder">No Image Selected</div>
            )}
          </div>

          <div className="prediction-card">
            <h2>Detection Result</h2>
            {prediction ? (
              <div className="prediction-result">
                <p className="prediction-class">Disease Class:</p>
                <p className="prediction-class-value">{prediction.class}</p>
                <p className="confidence">Confidence:</p>
                <p className="confidence-value">{prediction.confidence.toFixed(2)}%</p>
              </div>
            ) : (
              <div className="placeholder">Upload an image and press "Detect Disease"</div>
            )}
          </div>
        </div>
      </main>
      
      <footer className="app-footer">
        <p>&copy; 2024 PlantView | AI-Powered Plant Disease Detection</p>
      </footer>
    </div>
  );
}

export default App;