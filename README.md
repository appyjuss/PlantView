# PlantView 🌱

PlantView is a web application that allows users to upload plant images and detect potential diseases using trained Convolutional Neural Network (CNN) models. The system demonstrates how AI can be applied in agriculture to improve crop monitoring, reduce yield losses, and support smarter farming practices.

---

## Features

* Upload images of plants for disease detection
* Machine learning backend with CNN-based classification models
* React frontend with a simple and user-friendly interface
* Flask backend for handling API requests and ML inference

---

## Tech Stack

* **Frontend**: React
* **Backend**: Flask
* **Machine Learning**: CNN models trained on plant disease datasets
* **Languages**: Python, JavaScript

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/appyjuss/plantview.git
cd plantview
```

### 2. Setup Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
flask --app .\main.py run --port=8080
```

### 3. Setup Frontend (React)

```bash
cd plantViewFrontend
npm install
npm start
```

### 4. Access the App

Open your browser at `http://localhost:3000`

---

## Project Goals

* Showcase how AI can be applied in agriculture
* Help farmers and researchers monitor crop health
* Explore the potential of CNNs in image classification for real-world use cases

---

## Future Improvements

* Expand dataset for more plant species and diseases
* Add visualization for prediction confidence levels
* Deploy the app in production with Docker/Kubernetes
