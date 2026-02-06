# 🚀 Deployment Guide

This project is containerized using **Docker**, making it easy to deploy to any cloud provider that supports containers (Render, Railway, Fly.io, AWS App Runner, etc.).

## 🐳 Docker (Local Run)

You can build and run the application locally to verify it works before deploying.

### 1. Build the image
```bash
docker build -t cloud-monitoring .
```

### 2. Run the container
```bash
# Run with .env file variables
docker run -p 8000:8000 --env-file .env cloud-monitoring
```

The API will be available at `http://localhost:8000/docs`.

---

## ☁️ Deploy to Render (Easiest & Free Tier)

[Render](https://render.com) is one of the easiest ways to deploy.

1. **Push your code** to GitHub.
2. Sign up for **Render**.
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Runtime: Select **Docker**.
6. Environment Variables:
   Add the following variables from your `.env` file:
   - `GEMINI_API_KEY`
   - `LANGFUSE_SECRET_KEY`
   - `LANGFUSE_PUBLIC_KEY`
   - `LANGFUSE_HOST`
7. Click **Create Web Service**.

Render will automatically build your Dockerfile and deploy it.

---

## 🚆 Deploy to Railway (Fastest)

[Railway](https://railway.app) is extremely fast and auto-detects Dockerfiles.

1. Install Railway CLI (optional) or go to [railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repository.
4. Railway will detect the `Dockerfile` and start building.
5. Go to **Variables** tab and add your API keys.
6. Go to **Settings** -> **Generate Domain** to get a public URL.

---

## 🚀 Deploy to Fly.io

1. Install `flyctl`.
2. Login: `fly auth login`.
3. Initialize: `fly launch` (detects Dockerfile).
4. Set secrets:
   ```bash
   fly secrets set GEMINI_API_KEY=... LANGFUSE_SECRET_KEY=...
   ```
5. Deploy: `fly deploy`.
