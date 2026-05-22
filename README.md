# AI Agents Workshop

A local-first workshop for building a multi-agent business assistant one agent at a time. The use case follows the FoundryIQ and Agent Framework demo pattern: an orchestrator routes employee questions to HR, Products, and Marketing specialist agents. Each exercise leaves you with a running version of the application.

## What You Build

- A local HR policy agent
- A local Products knowledge agent
- A local Marketing knowledge agent
- A local orchestrator that routes questions to specialists
- Optional observability with OpenTelemetry and Azure Application Insights for Microsoft Foundry review

## Workshop Flow

| Exercise | Outcome | Run Command |
| --- | --- | --- |
| 00 | Prepare the local environment | `python -m app.cli --help` |
| 01 | Run the HR agent | `python -m app.cli --agent hr --query "What is the PTO policy?"` |
| 02 | Add the Products agent | `python -m app.cli --agent products --query "Tell me about the fitness watch"` |
| 03 | Add the Marketing agent | `python -m app.cli --agent marketing --query "What campaigns are active?"` |
| 04 | Run the orchestrator | `python -m app.cli --query "Do we sell a fitness watch?"` |
| 05 | Run the web app with observability hooks | `uvicorn app.main:app --reload --port 8000` |

## Quick Start

```bash
cd ai-agents-workshop
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m app.cli --query "What is the PTO policy?"
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000 after starting Uvicorn.

## Publish the Workshop with GitHub Pages

This project is configured like the TechWorkshop site by using Jekyll and the `just-the-docs` theme.

1. Create a GitHub repository named `ai-agents-workshop`.
2. Update `_config.yml` with your GitHub organization or user name:

```yaml
url: https://<github-org-or-user>.github.io/ai-agents-workshop/
aux_links:
	"AI Agents Workshop on GitHub":
		- "https://github.com/<github-org-or-user>/ai-agents-workshop"
```

3. Push the project to the `main` branch.
4. In GitHub, open **Settings > Pages**.
5. Set **Build and deployment > Source** to **GitHub Actions**.
6. Run the `Deploy Jekyll with GitHub Pages dependencies preinstalled` workflow, or push a new commit to `main`.

The site entry point is `index.md`, and the workshop navigation is generated from the front matter in the `docs` folder.

## Optional Observability Setup

The app runs without Azure. To send traces to Application Insights, install the optional dependencies and set the connection string:

```bash
python -m pip install -e ".[observability]"
copy .env.sample .env
# Add APPLICATIONINSIGHTS_CONNECTION_STRING to .env
uvicorn app.main:app --reload --port 8000
```

See [docs/05_observability_ai_foundry.md](docs/05_observability_ai_foundry.md) for the full exercise.
