# 🚀 Deployment Guide (V2 - Streamlit)

This project is now a **Streamlit Dashboard** containerized using **Docker**.

## 🐳 Docker (Local Run)

### 1. Build the image
```bash
docker build -t cloud-monitoring-v2 .
```

### 2. Run the container
You MUST provide the `GOOGLE_API_KEY` for the Agent Chat to work.

```bash
docker run -p 8501:8501 \
  --env-file .env \
  -e GOOGLE_API_KEY="your-google-api-key" \
  cloud-monitoring-v2
```

Open your browser at `http://localhost:8501`.

---

## ☁️ Deploy to Render (Easiest & Free Tier)

1. **Push your code** to GitHub (branch `deploy_v2`).
2. Sign up for **Render**.
3. Create **New Web Service**.
4. Connect your repo.
5. Runtime: **Docker**.
6. **Environment Variables** (Required):
   - `GOOGLE_API_KEY`: Your Gemini API Key.
   - `LANGFUSE_SECRET_KEY`: (Optional)
   - `LANGFUSE_PUBLIC_KEY`: (Optional)
   - `LANGFUSE_HOST`: (Optional)
7. Render will detect the exposed port `8501` automatically.

---

## 🚆 Deploy to Railway

1. Click **New Project** -> **Deploy from GitHub**.
2. Railway detects the `Dockerfile`.
3. Go to **Variables** and set `GOOGLE_API_KEY`.
4. Railway will deploy and provide a URL.

---

## 🚀 Deploy to Fly.io

1. `fly launch`
2. It detects Dockerfile.
3. When asked if you want to set up a Postgres/Redis, say **No** (unless you need it).
4. `fly secrets set GOOGLE_API_KEY=...`
5. `fly deploy`
