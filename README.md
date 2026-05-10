# GenAI Governance Salesforce Prototype

This repository contains a Salesforce DX prototype for managing enterprise GenAI cloud service requests. It implements the Force.com platform configuration as metadata and uses Python scripts for runtime setup and smoke testing.

## Scope

The prototype demonstrates:

- Custom objects for business units, cloud models, GenAI requests, and risk assessments.
- Lookup and master-detail relationships.
- Validation rules for justification, budget control, cloud model selection, and risk assessment requirements.
- Custom profiles for Business User, Governance Officer, and Cloud Admin.
- Salesforce Flow automation for email notifications, review task creation, and deployment reminders.
- Python automation that uses the existing Salesforce CLI authorization.

## Project Structure

```text
force-app/main/default/
  applications/      Salesforce custom app metadata
  flows/             Record-triggered Flow metadata
  objects/           Custom objects, fields, relationships, and validation rules
  profiles/          Custom profile and admin access metadata
  tabs/              Custom object tabs
src/genai/
  salesforce_cli.py  Safe wrapper for Salesforce CLI JSON commands
  setup_demo.py      Creates demo users and sample records
  smoke_test.py      Verifies validation rules and task automation
```

## Prerequisites

- Salesforce CLI installed.
- A Salesforce Developer Edition org authorized in the Salesforce CLI.
- Python 3.12 or later.
- `uv` installed for dependency and command execution.

The default target org alias used by the scripts is `genai-dev-de`.

## Deployment

Set the target org:

```bash
sf config set target-org=genai-dev-de
```

Deploy the Salesforce metadata:

```bash
sf project deploy start --target-org genai-dev-de --source-dir force-app/main/default
```

## Runtime Setup

Create or verify demo users and seed records:

```bash
uv run python -m genai.setup_demo
```

Run smoke tests:

```bash
uv run python -m genai.smoke_test
```

## Quality Checks

Run the Python checks:

```bash
uv run ruff format src
uv run ruff check src
uv run mypy src
```

## Notes

- Salesforce credentials and tokens are not stored in this repository.
- Local Salesforce CLI state under `.sf/` and `.sfdx/` is ignored.
- The `.env` file is ignored and is not required for the current Salesforce CLI based automation.
