Prompt:

```
With all these context, one specific question I need help is: what workflow/orchestration solution I should use? To do a measurement, I need to do a long running process, including outer loop and inner loop. 

Outer loop: 

- First, some prep work, such as run tests (which will be remotely, like in github action, or a buildkite build) a few times, to get 1) code coverage data, 2) test flakiness data
- Given a number N (e.g. we want to measure it with 200 mutants), enumerate N different mutants. 
- For each mutant, run the inner loop. 

The input of the outer loop is 
- The repo (including a commit, because we need to do the rest on a particular version of the repo)
- The tests (it could be unspecified/default, or a specific set like a specific pytest command with some parameters)
- The number N, i.e. how many mutants we want to use

The output of the outer loop is: 
- A high level results: what % of the N mutants are detected
- Detailed results. 

Inner loop:

- Create a pull request with the mutant
- Run the tests (including auto rerun on failed tests)
- Get the test results
- Analyze the test result: we need to look at pass/failure, and also look at it in conjunction with the test flakiness data. 
- Eventually, conclusion: whether this mutant is detected or not. 

The input of the inner loop is: the repo and the version, the tests, the mutant. 
The output of the inner loop is: whether the mutant is detected or not, plus details (e.g. which tests failed). 


This whole process of running 1 test effectiveness measurement, including the outer loop and inner loop, is a long running process (we can call it a workflow). It might take hours to run, if not days. It might get disrupted. It might need pause, resume, start-over, rerun (a part), etc. A typical workflow thing (just like a "workflow" in Argo Workflows https://argoproj.github.io/workflows/, or a github workflow --- these defined in the .github/workflows folder in a repo). 

I am not sure what exact technology I should use to run such a long running process. 

Argo Workflows is definitely an option. I can have my own k8s cluster (could be EKS in AWS), then run Argo Workflows in that cluster. I used it before (to run other long running processes).

I am wondering if there is any other technologies available. 

A few things will be nice:

1. Less operational overhead will be nice. I am fine with EKS and Argo Workflows. But still, less infrastructure work, the better. 

2. Multi tenancy. Because tinybug is multi tenancy. Let's say now three customers (Robinhood, Coinbase, Stripe) have onboarded to tinybug. They will access tinybug.ai via tinybug.ai/robinhood, tinybug.ai/coinbase, tinybug.ai/stripe. Robinhood people will onboard their repos and tests in tinybug.ai/robinhood, and see their results in tinybug.ai/robinhood too. They will also see the running measurements, as well as the finished ones. tinybug.ai itself will have multi tenancy access control so that Robinhood people won't see anything under tinybug.ai/coinbase. I want the multi tenancy access control over the long running measurement process/workflow as well. 

These are the two most important factors. 

Other factors (less important that the above two) include:
- Cost
- Operability/observability/stability/etc


With all these, please give me some recommendation regarding the technical solution to run the long running process of test effectiveness measurement. 
```

Answer:

# Recommendation: Workflow Orchestration Solution for Tinybug.ai

## ✅ Recommended Solution: Temporal

[Temporal](https://temporal.io) is a battle-tested, developer-friendly, open-source workflow engine ideal for building long-running, stateful workflows like Tinybug’s test effectiveness measurement.

---

## 🧠 Why Temporal Fits Tinybug.ai

| Requirement                          | Temporal Support                                                                 |
|--------------------------------------|----------------------------------------------------------------------------------|
| Long-running workflows               | ✅ Designed for multi-hour/day workflows with durability and retries             |
| Pause/resume/retry/failure recovery | ✅ First-class features with deterministic replays                               |
| Multi-tenancy                        | ✅ Supports isolated **namespaces** per tenant (e.g. robinhood, coinbase, etc.)  |
| CI integration (GitHub, Buildkite)  | ✅ Easily orchestrates external systems via activities                           |
| Low infra overhead                   | ✅ Use **Temporal Cloud** (fully managed) or self-host minimal infra             |
| Observability                        | ✅ Built-in web UI, CLI, logs, metrics, step-level visibility                    |
| Cost efficiency                      | ✅ Only orchestrates — CI execution cost handled in user infra                   |
| Programming model                    | ✅ Code-first (TypeScript, Go, Python, Java SDKs)                                |

---

## 🛠️ Mapping to Tinybug’s Outer/Inner Loops

### Outer Workflow: `RunMeasurement`
- **Input**: Repo + commit, test command/config, number of mutants `N`
- **Activities**:
  - `RunBaselineTestsForCoverageAndFlakiness`
  - `EnumerateMutants(N)`
  - For each mutant:
    - Start **inner workflow**: `RunMutationTrial(mutant)`

### Inner Workflow: `RunMutationTrial`
- **Input**: Repo + commit, test config, 1 mutant
- **Activities**:
  - `CreateMutantBranch`
  - `CreatePullRequest`
  - `TriggerCIBuildAndWait`
  - `FetchTestResults`
  - `EvaluateMutationOutcome` (considering flaky test profile)

---

## 🆚 Comparison: Argo Workflows vs Temporal

| Feature                        | Argo Workflows                        | Temporal                               |
|-------------------------------|----------------------------------------|----------------------------------------|
| Infra overhead                | Requires K8s cluster, CRDs, etc.       | Temporal Cloud (managed) or self-host  |
| Programming model             | YAML-based (K8s CRDs)                  | Code-based (Go, TS, etc.)              |
| Stateful/durable workflows    | Partially (via K8s patterns)           | ✅ Fully stateful + resumable           |
| Multi-tenancy                 | Not native (requires custom infra)     | ✅ Namespaces with isolated workflows   |
| GitHub/CI integration         | Custom plugins or scripts              | ✅ Easy via external activities         |
| Observability/debuggability   | Decent (UI + Prometheus)               | ✅ Strong CLI + UI + stack traces       |
| Best for                      | Data pipelines, K8s-native workloads   | Long-running service orchestration     |

---

## 🚀 Getting Started

### Option 1: **Temporal Cloud (Recommended)**
- Fully managed: no infra ops
- Create namespaces for each tenant
- Pricing: pay-as-you-go

### Option 2: **Self-host Temporal**
- Deploy via Helm on EKS, ECS, or EC2
- Requires a Postgres or MySQL backend
- Still relatively lightweight (compared to full Argo setup)

---

## 🟢 Summary

Use **Temporal** — ideally **Temporal Cloud** — as the orchestration backend for Tinybug's long-running, multi-tenant measurement workflows.

It will give you:
- Resilient, resumable workflows
- Clear multi-tenancy isolation
- Great observability
- Clean developer experience
- Low operational burden

