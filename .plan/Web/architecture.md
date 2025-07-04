# Web Architecture and Tech Stack for Tinybug.ai

Tinybug requires two distinct web experiences:

1. **Logged-Out Public Site**  
   - Purpose: Marketing, documentation, onboarding flow  
   - Access: Public, no login  
   - Content: Static

2. **Logged-In App (User Portal)**  
   - Purpose: Configure repos/tests, view mutation test results  
   - Access: Authenticated per-tenant (e.g. `/robinhood`, `/coinbase`)  
   - Content: Interactive, dynamic, user- and data-specific  

---

## 🔹 Public Site (Logged-Out)

### Requirements

- SEO-friendly
- Fast to load
- Easy to deploy and maintain
- Supports docs and landing pages

### Recommended Stack

| Component       | Tech                                      |
|-----------------|-------------------------------------------|
| Static site gen | [Next.js](https://nextjs.org/) in static export mode *(recommended)*<br>or [Hugo](https://gohugo.io/), [Astro](https://astro.build/) |
| Hosting         | [Vercel](https://vercel.com/), [Netlify](https://www.netlify.com/), or GitHub Pages |
| Auth (optional) | Clerk/Auth0/etc. if you want to support sign-in links |

You can also write docs in Markdown and render them using something like [Nextra](https://nextra.site/) or [Docusaurus](https://docusaurus.io/).

---

## 🔹 Logged-In Site (User Portal)

### Overview

A full-featured web app where users interact with Tinybug's core functionality: onboarding repos, viewing results, triggering measurements, etc.

### Architecture

- **Frontend**: React + Next.js (TypeScript)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **DB Access Layer**: SQLModel + Alembic
- **Workflow Engine**: Temporal Cloud (via Python SDK)
- **Auth**: Clerk.dev or FastAPI+JWT
- **CI Integration**: GitHub Actions (for PoC/MVP)

---

## 🧱 Tech Stack Details

### Frontend

| Component  | Tech                         |
|------------|------------------------------|
| Framework  | [React](https://reactjs.org/) |
| Rendering  | [Next.js](https://nextjs.org/) for routing, SSR/CSR |
| Language   | TypeScript                   |
| Auth       | Clerk.js or custom JWT flow  |
| Data Fetch | `fetch`, Axios, or SWR       |
| Hosting    | Vercel / Netlify             |

### Backend

| Component  | Tech                         |
|------------|------------------------------|
| Web API    | [FastAPI](https://fastapi.tiangolo.com/) |
| Language   | Python 3.11+                 |
| DB         | PostgreSQL                   |
| DB Layer   | [SQLModel](https://sqlmodel.tiangolo.com/) + [Alembic](https://alembic.sqlalchemy.org/) |
| Auth       | FastAPI JWT auth or Auth0/Clerk integration |
| Queue/Jobs | [Temporal Cloud](https://temporal.io/cloud) |
| Hosting    | Railway / Fly.io / AWS       |

---

## 🔗 Communication Between Frontend & Backend

The frontend (Next.js) will call FastAPI endpoints using standard HTTP:

```ts
const res = await fetch("/api/results/123");
const data = await res.json();
