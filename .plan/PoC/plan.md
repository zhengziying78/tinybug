Prompt:

```
give me a detailed PoC milestone plan with timeline and deliverables
```

Answer: 

# Tinybug.ai PoC Milestone Plan

## Overview

Focus:  
- Mutation testing proof of concept for one language (Python or Golang)  
- Simple mutators, integration with GitHub Actions  
- Use Temporal Cloud for workflow orchestration  
- Basic results UI for a single tenant  

---

## Milestones & Timeline

| Milestone                       | Duration | Deliverables                                   | Description                                      |
|--------------------------------|----------|-----------------------------------------------|-------------------------------------------------|
| **1. Project Setup & Research** | 1 week   | - PoC repo scaffold<br>- Select language (Python or Golang)<br>- Evaluate mutator libs (MutPy, Go mutator, etc.)<br>- Temporal Cloud account setup | Prepare foundations, confirm tooling and environment choices |
| **2. Mutation Generation Prototype** | 2 weeks  | - Working mutator generating simple mutants<br>- Mutation applied to test repo branch<br>- Ability to generate ~10 mutants per run | Implement basic mutation logic using existing libs or simple custom mutators |
| **3. GitHub Actions Integration** | 1 week   | - GitHub Actions workflow triggered by PR<br>- Tests run on mutated code branches<br>- Collect test pass/fail results | Set up CI pipeline to run tests on mutants and report results |
| **4. Temporal Workflow Orchestration** | 2 weeks  | - Temporal workflows orchestrating outer and inner loops<br>- Outer loop: coverage & mutant enumeration<br>- Inner loop: create PR, trigger tests, fetch results, analyze<br>- Basic error handling and retry | Implement the long-running measurement orchestration on Temporal |
| **5. Result Aggregation & Basic UI** | 1 week   | - Simple web UI or CLI<br>- Show overall mutation score<br>- List mutants with pass/fail<br>- View mutant details (diff + test results) | Provide minimal user interface to present results to the tenant |
| **6. Basic Tenant Setup**       | 1 week   | - Support single tenant namespace in Temporal<br>- Tenant-specific URLs (e.g., `/poctenant`)<br>- Basic access control enforcement | Implement minimal multi-tenancy support for the PoC |
| **7. Testing & Validation**     | 1 week   | - End-to-end test runs<br>- Validate mutation scoring accuracy<br>- Verify Temporal workflows’ resilience | Test the PoC system and fix issues |
| **8. Documentation & Demo**     | 1 week   | - PoC documentation<br>- Demo script<br>- Prepare for stakeholder review | Finalize docs and demo materials |

---

## Total Duration: ~10 weeks

---

## Notes

- Timeline can be compressed if resources allow.  
- Priority is working end-to-end flow, even if parts are minimal or hardcoded.  
- Focus on ease of iteration for MVP phase.  
- Can swap out GitHub Actions for another CI in MVP.  
- Mutators kept simple initially, extensible later.  

---

*Let me know if you want me to help draft MVP milestones next!*



----------


# 🧪 Updated Proof of Concept (PoC) Plan for Tinybug.ai

This PoC aims to demonstrate end-to-end viability of mutation-based test effectiveness measurement using real repos and real CI, with a full stack implementation including web UI, backend, workflow orchestration, and multi-tenant support.

---

## ✅ Scope

- End-to-end mutation testing on one example repo (e.g. Python project with pytest)
- Use GitHub Actions to run tests in the repo’s own CI environment
- Use Temporal to orchestrate the workflow (outer and inner loops)
- Web UI and API for one tenant (e.g. `tinybug.ai/orgs/example`)
- Deployed to staging and production environments
- Secrets and configuration managed securely

---

## 🧩 Components & Deliverables

### 1. **Mutator Engine**

- Use an existing mutator tool (e.g. [`mutmut`](https://github.com/boxed/mutmut) or [`mutpy`](https://github.com/mutpy/mutpy)) for Python
- Implement logic to:
  - Generate a set of mutants
  - Apply a single mutant to a clone of the repo
  - Push mutated code to a temporary branch
- Minimal mutation patterns (e.g. arithmetic operator replacement, conditional flip)

---

### 2. **Workflow Orchestration (Temporal)**

- Use **Temporal Cloud**
- Define workflows:
  - **Outer loop**: prepare coverage/flakiness, generate N mutants, run inner loop for each
  - **Inner loop**: mutate, push, run tests, fetch results, classify mutant
- Set up one **namespace** per environment (`tinybug-dev`, `tinybug-staging`, `tinybug-prod`)
- Temporal Workers run in **Fly.io**, written in Python (using `temporalio` SDK)

---

### 3. **Test Runner Integration**

- GitHub Actions-based integration
- For each mutant:
  - Push to a dev branch (e.g. `tinybug/mutant-123`)
  - Wait for GitHub Actions to run
  - Use GitHub API to fetch test results (status + failure details)
- Later: Add support for Buildkite

---

### 4. **Backend API (FastAPI)**

- Backend service to:
  - Manage organizations, repos, runs
  - Trigger measurement runs
  - Fetch run details and mutant status
- Secure, tenant-aware routing (e.g. `/api/orgs/robinhood`)
- Serve config and secrets from env vars via `pydantic` settings
- Fly.io deployment with environment-specific secrets

---

### 5. **Web Frontend (Next.js + React)**

- UI served from `tinybug.ai` (prod) and `staging.tinybug.ai` (staging)
- Views for:
  - Org dashboard
  - Repo setup form
  - View all runs
  - View individual run + list of mutants (caught/uncaught)
- Friendly URLs: `/orgs/robinhood/results/:runId`, etc.
- API requests proxied to FastAPI backend via `/api` path

---

### 6. **Secrets Management**

- Use **Doppler** or **AWS Secrets Manager**:
  - Secrets per environment (`dev`, `staging`, `prod`)
  - Secrets per org (e.g. GitHub tokens)
- Local dev: use Doppler CLI or `.envrc` with `direnv`
- CI and deploy: inject secrets via Doppler → Fly.io/Vercel

---

### 7. **Infrastructure & Hosting**

| Component        | Hosted On        |
|------------------|------------------|
| Web frontend     | Vercel           |
| API backend      | Fly.io           |
| DB (Postgres)    | Supabase         |
| Workflow Engine  | Temporal Cloud   |
| Secrets          | Doppler or AWS   |
| Domain           | Cloudflare (`tinybug.ai`) |

- Environments:
  - `tinybug.ai` (prod)
  - `staging.tinybug.ai` (staging)
- Deployment via Git branches:
  - `main` → production
  - `staging` → staging

---

## 🧪 Sample Flow (End to End)

1. User from `orgs/robinhood` logs in
2. Configures repo and GitHub token
3. Starts a test effectiveness measurement
4. Backend triggers a Temporal outer workflow:
   - Gets coverage + flakiness
   - Creates 50 mutants
   - Runs each inner workflow: mutate → push → wait → fetch → analyze
5. UI shows measurement progress and results:
   - 32/50 mutants caught
   - View caught/uncaught list
   - View details of a mutant and corresponding test failures

---

## 🧹 Nice-to-Have (Optional for PoC)

- GitHub App onboarding flow (vs raw token)
- Flaky test detection logic
- Coverage analysis logic (e.g. skip uncovered lines)
- UI polish / theming
- JSON export of results

---

## 🔐 Secrets Needed for PoC

| Purpose                  | Secret Name / Example                            |
|--------------------------|--------------------------------------------------|
| GitHub API access        | `GITHUB_PAT` or GitHub App token                 |
| DB access                | `POSTGRES_URL`                                   |
| Temporal Cloud access    | `TEMPORAL_MTLS_CERT`, `TEMPORAL_MTLS_KEY`       |
| OAuth for login          | `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`       |
| Vercel & Fly deploy keys | Stored in GitHub Actions or Doppler             |

---

## ✅ Summary

The updated PoC plan includes a complete loop from repo config to mutant result viewing — with modern, secure, deployable architecture. It’s focused, practical, and lays a strong foundation for future MVP expansion.
