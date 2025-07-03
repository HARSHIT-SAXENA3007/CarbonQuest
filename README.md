# 🌱 CarbonQuest — Intelligent Carbon Footprint Analyzer

CarbonQuest is a full-stack AI-powered application that helps users estimate their monthly carbon footprint based on transport, electricity, food, and shopping habits. It provides personalized suggestions to reduce emissions and clusters user data to visualize environmental impact trends using KMeans and PCA. Built with Flask (backend), React (frontend), and Google Gemini API (AI suggestions).

---

## 📸 Project Preview

Users input lifestyle data → app returns carbon emission stats → AI suggestion → download cluster graph of emission behavior.

---

## 🚀 Features

- Calculates carbon footprint based on user habits.
- Uses Gemini AI to suggest ways to reduce emissions.
- Clusters similar users using KMeans & PCA and generates downloadable visual plots.
- Clusters are updated and enhanced in real time according to the data prvoided by the users.
- Gemini AI also provides a detailed summary of the visual plots.
- Clean dark-themed UI built with React.

---

## 🧠 Technologies Used

### Frontend:
- React.js
- Axios
- HTML/CSS

### Backend:
- Flask (Python)
- Flask-CORS
- Pandas, NumPy
- Scikit-learn
- Matplotlib
- Google Generative AI API

---

## 📦 Installation Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/CarbonQuest.git
cd CarbonQuest
```

### 2. Install the requirements

```bash
pip install -r requirements.txt
```

### 3. Set up Environment Variable

```bash
GEMINI_API_KEY=your_api_key_here
```

### 4. Start Flask Server

```bash
python app.py
```

### 5. Start React Frontend

```bash
cd carbon-frontend
npm install
npm start
```



