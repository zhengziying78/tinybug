# Staging / Canary Environment Strategy for Tinybug.ai

## 🧭 Goals

- ✅ Lightweight and inexpensive
- ✅ Avoid breaking production for other users
- ✅ Full-stack (frontend + backend + DB + Temporal)
- ✅ Git-based, easy to deploy
- ✅ Optional internal-only access

---

## 🧪 Environments Overview

| Environment | Domain                     | Purpose                       |
|-------------|----------------------------|-------------------------------|
| Production  | `tinybug.ai`               | Live site for users           |
| Staging     | `staging.tinybug.ai`       | Internal testing, validation  |

> _Optional_: You can use sub-subdomains like `app.staging.tinybug.ai` and `api.staging.tinybug.ai`, or just `staging.tinybug.ai` with routing inside the app.

---

## 🌍 Public Site (Landing Page)

- You **do not need staging** for this unless you’re testing a marketing campaign.
- If you do:
  - Set up a separate Cloudflare Pages site
  - Use `preview.tinybug.ai` or `dev.tinybug.ai`
  - Use a separate Git branch (`preview`) for this

---

## 🔐 Logged-In App (Staging)

### 1. **Frontend**

- Deployed via Vercel with a second environment: `staging.tinybug.ai`
- Triggered by a separate branch (e.g. `staging` or `main` if production uses `release`)
- Connected to staging API (`https://api.staging.tinybug.ai`)
- Vercel supports multiple environments natively

### 2. **Backend**

- Deploy a second Fly.io app:
  - `tinybug-api-staging`
  - Domain: `api.staging.tinybug.ai`
- Separate `.env.staging` file for config
- Isolated from production DB + workflows

### 3. **Database**

- Create a separate **Supabase project** (free tier)
- Used only by staging API
- Allows safe DB schema testing, data manipulation

### 4. **Temporal (Optional but Nice)**

- Use a separate **namespace** in Temporal Cloud (e.g. `staging`)
- Reuse the same Temporal account
- Lets you test workflows without polluting prod state

---

## 🌐 DNS Setup (Cloudflare)

| Record               | Points to                        |
|----------------------|----------------------------------|
| `staging.tinybug.ai` | Vercel frontend preview URL      |
| `api.staging.tinybug.ai` | Fly.io staging API            |

---

## 🚀 Deployment Flow

| Action                      | Effect                                      |
|-----------------------------|---------------------------------------------|
| Push to `main`              | Deploys to **production**                  |
| Push to `staging`           | Deploys to **staging** frontend/backend     |
| Merge `staging` → `main`    | After testing is validated                  |

---

## 🔐 Access Control for Staging

- **Basic auth**: Protect staging via Vercel/Fly with a password
- **Whitelist IPs**: Or limit access by IP (e.g. office/VPN only)
- **Staging accounts only**: Require test credentials via Clerk or mock auth

---

## 🧰 Tooling Notes

| Component   | Setup Details                              |
|-------------|---------------------------------------------|
| **Vercel**  | Use "Preview Deployments" or named environments (`staging`) |
| **Fly.io**  | Deploy to a separate app name with its own config |
| **Supabase**| Create second project, configure `.env.staging` |
| **Temporal**| Use separate namespace (`staging`)          |

---

## ✅ Summary

You only need:

- 1 extra Fly.io app (FastAPI backend for staging)
- 1 extra Supabase project (Postgres for staging)
- 1 extra Vercel environment (Next.js frontend for staging)
- 1 extra DNS subdomain (`staging.tinybug.ai`, etc.)
- (Optional) 1 extra Temporal namespace (`staging`)

This gives you a **safe, isolated staging setup** to test real integrations, with **minimal cost and effort** — perfect for pre-PMF startups.

