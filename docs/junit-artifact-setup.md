# Capturing Pytest JUnit Reports in GitHub Actions

This guide explains how to configure a repository so every GitHub Actions run publishes the pytest JUnit XML report as a workflow artifact.

## 1. Update the Test Command

Ensure the command that invokes pytest generates a JUnit XML file and writes it to a known location, for example `pytest-results/junit.xml`:

```make
@mkdir -p pytest-results
$(VENV_BIN)/python -m pytest $(COV) --junitxml=pytest-results/junit.xml
```

Adjust the command to match your project’s tooling (e.g., `python -m pytest`, `poetry run pytest`, etc.).

## 2. Upload the Report in the Workflow

Add an artifact upload step to the GitHub Actions workflow after the tests run. The example below assumes your tests live in `.github/workflows/tests.yml`.

```yaml
- name: Upload pytest JUnit report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: pytest-junit
    path: pytest-results/junit.xml
    if-no-files-found: warn
```

Key details:
- `if: always()` uploads the report even when tests fail.
- `if-no-files-found: warn` keeps the workflow from failing if the file is missing due to an early crash.

## 3. Verify the Artifact

After pushing the changes, open the workflow run in the **Actions** tab. Under the run’s summary page you should see an **Artifacts** section with an entry such as `pytest-junit`. Downloading the artifact confirms the XML file is being stored (for example, run [`18618409274`](https://github.com/zhengziying78/demo-httpie-cli/actions/runs/18618409274) uploaded `pytest-junit.zip`, 15&nbsp;KB, artifact ID `4307818501`).

<img width="1787" height="943" alt="image" src="https://github.com/user-attachments/assets/96fb8b50-44eb-434d-9d91-5f60ad3724bb" />

Once the artifact is available, automation (e.g., Temporal workflows) can fetch and parse `junit.xml` instead of scraping raw logs.
