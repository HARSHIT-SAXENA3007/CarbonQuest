# CarbonQuest

CarbonQuest is a full-stack carbon footprint analyzer. Users enter monthly lifestyle data for transport, electricity, food, and shopping, and the app calculates emissions, shows the highest-impact category, generates reduction suggestions, and places the user into a simple emissions cluster using KMeans and PCA.

## Stack

- Backend: Flask, pandas, scikit-learn, matplotlib
- Frontend: React, Axios
- AI summaries: Gemini API

## What Was Fixed

- Frontend requests no longer hardcode `http://127.0.0.1:5000`
- The Flask app now exposes stable API routes under `/api/*`
- Flask can serve the React production build for single-service deployment
- The Gunicorn entry point now points at the actual application object
- Clustering no longer crashes when the dataset has too few rows
- Gemini calls now use the current stable model path `gemini-2.5-flash`

## Local Development

### 1. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd carbon-frontend
npm install
cd ..
```

### 3. Configure environment variables

Set these in your shell or hosting platform:

```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

`GEMINI_MODEL` is optional because the app already defaults to `gemini-2.5-flash`.

### 4. Run the backend

```bash
python application.py
```

The Flask API will be available at `http://127.0.0.1:5000`.

### 5. Run the frontend in development

```bash
cd carbon-frontend
npm start
```

The React dev server uses the `proxy` setting in `carbon-frontend/package.json`, so frontend requests to `/api/*` are forwarded to Flask automatically.

## Production Build

Build the frontend:

```bash
cd carbon-frontend
npm run build
cd ..
```

After that, start Flask:

```bash
python application.py
```

Flask will serve the built React app and the API from the same origin.

## Split Deployment: Vercel + Render

This is the cleanest setup for the current repo:

- Deploy `carbon-frontend` to Vercel
- Deploy the Flask API to Render

### Backend on Render

Render supports Flask apps served with Gunicorn. This repo includes [render.yaml](/abs/path/C:/Users/Harshit%20Saxena/CarbonQuest/render.yaml:1), which defines the web service.

Set these Render environment variables:

```bash
GEMINI_API_KEY=your_api_key_here
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

The backend start command is:

```bash
gunicorn application:application
```

After deploy, your API will be available at a Render URL such as:

```bash
https://carbonquest-api.onrender.com
```

### Frontend on Vercel

Vercel supports Create React App projects directly. Import this repository as a Vercel project and set the Root Directory to `carbon-frontend`.

Set this Vercel environment variable:

```bash
REACT_APP_API_URL=https://your-render-api.onrender.com
```

Then redeploy the frontend so the CRA build picks up the variable.

### Local Dev vs Hosted

- Local dev can keep using the CRA proxy in `carbon-frontend/package.json`
- Vercel builds use `REACT_APP_API_URL`
- If `REACT_APP_API_URL` is not set, the frontend falls back to relative `/api/*` paths

## Single-Service Deployment

If you want to keep deploying the whole app as one service instead, you can still build the frontend and serve it from Flask:

```bash
cd carbon-frontend
npm run build
cd ..
gunicorn application:application
```

## API Endpoints

- `GET /api/health`
- `POST /api/calculate`
- `GET /api/cluster-plot`
