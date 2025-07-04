Prompt:

```
Very nice. So, to confirm my understanding correctly, tinybug will have an account in temporal cloud, and then when Robinhood onboards to tinybug, tinybug will create a robinhood namespace in tinybug's temporal cloud account? And Coinbase will be another namespace, and Stripe will also be another namespace, which are all in the same tinybug account in Temporal Cloud?
```

Answer:

# Temporal Cloud Multi-Tenancy Model for Tinybug.ai

## How Tinybug Uses Temporal Cloud for Multi-Tenancy

- Tinybug will have a **single Temporal Cloud account**.
- Within that account, multiple **namespaces** will be created.
- Each customer (tenant) will get their **own namespace**, for example:
  - `robinhood`
  - `coinbase`
  - `stripe`

## What a Namespace Provides

- Logical isolation of workflows, activities, queues, and history.
- Separate resource quotas and rate limits.
- Separate access control boundaries (via Temporal Cloud policies or app-level enforcement).

## Benefits for Tinybug

| Feature                    | Description                                                   |
|----------------------------|---------------------------------------------------------------|
| Measurement job isolation  | Customer workflows run only within their namespace            |
| Failure containment        | Issues in one namespace don’t impact others                    |
| Tenant access control      | Tinybug controls UI/API access per tenant namespace            |
| Usage & billing separation | Usage metrics can be tracked per namespace for billing/reporting |

## Typical Implementation Flow

1. When a new customer signs up at `tinybug.ai/{customer}`, Tinybug creates a new Temporal namespace via Temporal CLI or API.
2. All workflows for that customer are submitted under their dedicated namespace.
3. Temporal workers poll tasks scoped to the customer's namespace, processing their workflows independently.

---

If needed, code snippets or architecture diagrams can be provided to illustrate namespace creation and workflow execution per tenant.
