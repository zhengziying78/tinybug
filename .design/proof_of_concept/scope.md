Prompt:

```
Now let's talk about PoC, proof of concept. 
I feel I am going to do a PoC first. Then a MVP (minimal viable product). Then more and more features. 
What's your thoughts on what the PoC should look like?
```

Answer:

# Proof of Concept (PoC) Plan for Tinybug.ai

## Objectives of PoC

- Validate core mutation testing workflow end-to-end  
- Demonstrate integration with external CI (e.g., GitHub Actions)  
- Prove feasibility of collecting and analyzing test results  
- Confirm Temporal-based orchestration approach works well  
- Deliver a minimal but meaningful user experience for one tenant  

---

## Suggested PoC Scope

### 1. Language & Repo

- Focus on **one language** initially (e.g., Python with pytest)  
- Use a **single public or private GitHub repo** (test repo you control)  

### 2. Mutation Generation

- Use an existing simple mutator (e.g., flip boolean conditions or arithmetic ops)  
- Generate a small fixed number of mutants (e.g., 10-20 mutants)  

### 3. Test Execution

- Use **GitHub Actions** workflow triggered by PR creation  
- Create a temporary branch or PR with mutated code  
- Wait for GitHub Actions to complete tests and collect pass/fail result  

### 4. Workflow Orchestration

- Use **Temporal Cloud** (or local Temporal) to orchestrate:  
  - Baseline coverage run  
  - Mutant generation loop  
  - Inner loop for mutation PR creation + test run + result fetch + evaluation  

### 5. Result Presentation

- Basic web UI or CLI to:  
  - Show overall mutation score (e.g., X out of Y mutants caught)  
  - List mutants with pass/fail status  
  - View details on one mutant (diff and test results)  

### 6. Multi-tenancy

- Support **only one tenant** for PoC (e.g., `tinybug.ai/poctenant`)  
- Namespace multi-tenancy setup in Temporal can be skipped or minimal  

---

## What to Skip / Defer for PoC

- Support for multiple languages  
- Complex flaky test handling or rerun logic  
- Sophisticated mutators or AI-generated mutants  
- Multi-tenant UI and strict access control  
- Cost optimization and advanced observability  
- Integrations beyond GitHub Actions  

---

## Why This Makes Sense

- Focus on proving your core value proposition: measuring test effectiveness by mutation testing.  
- Keep complexity low to deliver quickly and get feedback.  
- Validate Temporal as orchestration backend early.  
- Build a foundation to iterate into MVP with broader language support, more tenants, and enhanced features.

---

*If you want, I can help draft a detailed PoC milestone plan with timeline and deliverables.*
