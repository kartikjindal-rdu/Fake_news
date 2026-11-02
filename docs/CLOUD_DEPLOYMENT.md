# VERITAS AI — Cloud Deployment & Execution Guide

---

## 1. Local Development Setup

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### Step 1: Start FastAPI Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
> Backend will start at: `http://localhost:8000` (API Docs at `http://localhost:8000/docs`)

### Step 2: Start React Frontend
```bash
cd frontend
npm install
npm run dev
```
> Open your browser at: `http://localhost:3000`

---

## 2. Docker Multi-Container Deployment

Run both frontend and backend simultaneously with Docker Compose:

```bash
docker-compose up --build -d
```
- Web Application: `http://localhost:3000`
- REST API Server: `http://localhost:8000`

---

## 3. Cloud Provider Architecture (AWS / Azure / GCP)

- **Frontend Hosting**: AWS S3 + CloudFront / Vercel / Netlify.
- **Backend API**: AWS ECS (Fargate) / Azure Container Apps / Google Cloud Run.
- **Database**: AWS RDS PostgreSQL / Azure Database for PostgreSQL.
- **Storage**: AWS S3 for uploaded screenshots and PDF audit reports.
