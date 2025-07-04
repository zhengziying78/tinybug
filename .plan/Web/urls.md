# URL Strategy for Tinybug.ai

This strategy keeps everything under the same domain (`tinybug.ai`), uses clear paths to distinguish environments, tenants, and purposes (UI vs API). It’s clean, scalable, and dev-friendly.

---

## 🧭 Environment Separation

| Environment | Domain                  | Purpose                 |
|-------------|--------------------------|-------------------------|
| Production  | `tinybug.ai`             | Live for all users      |
| Staging     | `staging.tinybug.ai`     | Internal testing        |
| Dev (optional) | `dev.tinybug.ai`      | Personal/experimental   |

> Each environment runs a **full stack** (frontend, backend, DB, workers)

---

## 🌍 Logged-Out Pages

| URL                      | Description                     |
|--------------------------|---------------------------------|
| `/`                      | Marketing home page             |
| `/docs`                  | Documentation                   |
| `/pricing`               | Pricing page                    |
| `/blog`                  | Company blog                    |
| `/legal/terms`           | Terms of service                |
| `/legal/privacy`         | Privacy policy                  |

---

## 🔐 Logged-In App (Multi-Tenant)

| URL                                | Description                                |
|------------------------------------|--------------------------------------------|
| `/orgs/:org_slug`                  | Org dashboard (e.g. `tinybug.ai/orgs/stripe`) |
| `/orgs/:org_slug/repos`            | Repo configuration                         |
| `/orgs/:org_slug/results`          | Mutation test results                      |
| `/orgs/:org_slug/results/:run_id`  | Single test run detail                     |
| `/orgs/:org_slug/settings`         | Org settings                               |

> You can also support shorthand `/robinhood` as an alias for `/orgs/robinhood`.

---

## 🔌 API Endpoints (REST/JSON)

| Endpoint                          | Description                     |
|-----------------------------------|---------------------------------|
| `/api/health`                     | Health check                    |
| `/api/auth/login`                | Login/auth endpoint             |
| `/api/orgs/:org_slug/repos`       | CRUD for repos                  |
| `/api/orgs/:org_slug/results`     | List test results               |
| `/api/orgs/:org_slug/results/:id` | Get specific result             |
| `/api/orgs/:org_slug/config`      | Org-level config                |

> API paths match the UI paths structurally, just under `/api`.

---

## 🧪 Environment-Specific Versions

| Example                        | Notes                          |
|--------------------------------|--------------------------------|
| `tinybug.ai/orgs/robinhood`    | Production UI                  |
| `tinybug.ai/api/orgs/robinhood`| Production API                 |
| `staging.tinybug.ai/orgs/robinhood` | Staging UI                 |
| `staging.tinybug.ai/api/orgs/robinhood` | Staging API           |
| `dev.tinybug.ai/api/...`       | Dev environment (optional)     |

---

## ✅ Summary

| Dimension       | Strategy                            |
|------------------|-------------------------------------|
| **Environments** | Subdomains: `tinybug.ai`, `staging.tinybug.ai`, `dev.tinybug.ai` |
| **App vs. API**  | Path-based: `/orgs/...` for UI, `/api/...` for JSON endpoints |
| **Multi-tenancy**| Path param: `/orgs/:slug/...` (or shorthand `/robinhood`) |
| **Static vs. App** | Static site and app share domain (`tinybug.ai`) |
| **Ease of use** | Friendly, bookmarkable, logical paths |

---

## 👀 Bonus: Technical Tips

- On the frontend (Next.js), use [rewrites](https://nextjs.org/docs/app/building-your-application/configuring/rewrites) to proxy `/api/*` to your FastAPI backend.
- Backend (FastAPI) can mount all routes under `/api` using a prefix.
- Auth tokens can be scoped to org (included in session or header).
- Use wildcard TLS cert (`*.tinybug.ai`) via Cloudflare for simplicity.

---

This strategy keeps things elegant, dev-friendly, and production-ready from day one — without being overengineered.
