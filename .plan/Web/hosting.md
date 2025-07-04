# Hosting Architecture for Tinybug.ai

This document outlines the hosting and deployment strategy for Tinybug.ai, covering both the **public logged-out site** and the **logged-in application**. The goals of this architecture are:

- ✅ Low cost
- ✅ Reasonable monitoring and observability
- ✅ Simple rollout and updates (Git-based)
- ✅ Leverages Cloudflare for DNS and security
- ✅ Scalable for SaaS-style multi-tenant usage

---

## 🧭 Overview

| Component        | Platform         | Purpose                          |
|------------------|------------------|----------------------------------|
| Public site      | Cloudflare Pages | Marketing, documentation         |
| Logged-in app UI | Vercel (Next.js) | Multi-tenant frontend UI         |
| Backend API      | Fly.io (FastAPI) | REST API for app logic           |
| Database         | Supabase (Postgres) | Metadata storage                |
| Background jobs  | Fly.io or EC2    | Temporal workers                 |
| Auth             | Clerk.dev or FastAPI+JWT | User authentication    |
| Domain + DNS     | Cloudflare       | HTTPS routing + DNS management   |

---

## 🌐 Domain Routing (via Cloudflare)

You already own `tinybug.ai` via Cloudflare. We'll use subdomains to route traffic:

| Subdomain         | Target                    | Purpose              |
|-------------------|---------------------------|----------------------|
| `tinybug.ai`      | Cloudflare Pages          | Public site (static) |
| `app.tinybug.ai`  | Vercel-hosted frontend    | Logged-in UI         |
| `api.tinybug.ai`  | Fly.io-hosted FastAPI API | Backend service      |

All DNS and HTTPS are managed via **Cloudflare DNS** and **Cloudflare TLS certificates**.

---

## 🌍 Public Site Hosting

### Platform: **Cloudflare Pages**

- Static hosting for landing pages, docs, blog, etc.
- Supports frameworks like Next.js (static export), Hugo, Astro, etc.
- CDN-cached and highly performant
- **Free tier** includes 100k requests/day and 1k builds/month

### Deployment Flow

- Write content in Markdown or JSX
- Push to GitHub `main` branch
- Cloudflare auto-builds and deploys to `tinybug.ai`

---

## 🔐 Logged-In App Hosting

### Frontend (UI)

- Framework: **React + Next.js**
- Hosted on: **Vercel**
- Deploys from: GitHub repo
- Multi-tenant routing handled in-app (e.g. `/robinhood`, `/coinbase`)

### Backend (API)

- Framework: **FastAPI (Python)**
- Hosted on: **Fly.io**
- Exposes REST APIs under `/api`
- Connected to PostgreSQL DB
- Handles business logic, repo config, workflows, etc.

### Deployment Flow

- Push code to GitHub (e.g. `main`)
- Vercel builds frontend and deploys `app.tinybug.ai`
- Fly.io deploys backend from Dockerfile (can be CI/CD or manual)

---

## 🗃️ Database

### Platform: **Supabase**

- Managed **PostgreSQL**
- Free tier with generous limits
- Comes with:
  - SQL editor + dashboard
  - Optional realtime + auth (can disable)
- Use with: SQLModel + Alembic for schema migration

---

## ⚙️ Background Workers

### Platform: **Fly.io** or lightweight EC2 instance

- Run Temporal Python SDK workers
- Workers connect to **Temporal Cloud**
- Minimal CPU/RAM needed
- Deploy via Docker or virtualenv + supervisor

---

## 🛠 Observability & Monitoring

| Tool              | Used For                       |
|-------------------|--------------------------------|
| Cloudflare Analytics | Public site traffic         |
| Vercel Logs & Analytics | Frontend performance    |
| Fly.io Logs & Metrics | Backend + worker monitoring |
| Temporal Web UI   | Workflow visibility and debugging |
| Sentry (optional) | Frontend + backend error tracking |
| Logtail (optional) | Structured logs and alerts   |

---

## 💡 Summary

| Layer              | Tech/Platform        |
|--------------------|----------------------|
| Public site        | Cloudflare Pages     |
| Frontend (UI)      | Vercel (React + Next.js) |
| Backend API        | FastAPI on Fly.io    |
| Database           | Supabase (PostgreSQL)|
| Background workers | Fly.io / EC2         |
| Orchestration      | Temporal Cloud       |
| Auth               | Clerk.dev or FastAPI+JWT |
| DNS + TLS          | Cloudflare           |

---

## 🧪 Git-Based Workflow

All major components support Git-based deployment:

- Push to `main` (or `production`) on GitHub
- Triggers build and deploy:
  - Cloudflare → Public site
  - Vercel → Frontend
  - Fly.io → Backend
- Enables tight feedback loop and minimal manual effort

---

This architecture gives you a low-cost, reliable, and maintainable SaaS deployment setup with modern tooling and strong Python support.
