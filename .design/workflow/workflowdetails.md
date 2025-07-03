Prompt:

```
How shall we expose the workflow details to the users? For example, are we going to redirect Robinhood people to Temporal Cloud? Or, when Robinhood people wants to see workflow details (e.g. steps, the current steps, details in a step, etc.), tinybug fetches the details from Temporal Cloud (via Temporal API?) and then display it to Robinhood people on tinybug.ai/robinhood page?
```

Answer:

# Exposing Workflow Details to Tinybug Users

## Should we redirect users to Temporal Cloud UI?

**No, it's better not to redirect users to Temporal Cloud’s UI because:**

- **Consistent Branding & UX:** Keep users within tinybug.ai for a seamless experience.
- **Access Control:** Temporal Cloud UI is intended for operators; managing tenant-specific user access there is complex.
- **Customization:** Tinybug may want to tailor workflow information presentation and integrate with other features.

---

## Recommended Approach: Proxy Workflow Data Through Tinybug Backend

1. **Fetch Workflow Data from Temporal Cloud API**  
   Tinybug backend authenticates and queries Temporal Cloud for workflow executions, history, status, logs, etc.

2. **Process and Filter Data**  
   Backend translates raw workflow data into user-friendly formats, hides internal details, and enriches with Tinybug-specific metadata.

3. **Display in Tinybug UI**  
   Tenant-specific pages (e.g., `tinybug.ai/robinhood/workflows`) show workflow statuses, steps, logs, and allow searching/filtering/drilling down.

---

## Benefits

- **Single Pane of Glass:** Users stay within the Tinybug ecosystem without switching context.
- **Fine-grained Access Control:** Centralized enforcement of tenant-specific data visibility.
- **Customizable UI/UX:** Full control to adapt presentation and add value.
- **Security:** Limits exposure of internal orchestration details.

---

## Optional Enhancements

- Use or embed Temporal’s open-source UI components if desired.
- Build custom dashboards that combine workflow info with other Tinybug data.

---

*If needed, sample architecture diagrams or UI wireframes for this design can be created.*
