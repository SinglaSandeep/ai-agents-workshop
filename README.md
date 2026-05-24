# Pepsico AI Agents Workshop (L300)

> An end-to-end, hands-on workshop where you build a **multi-agent Pepsico
> business assistant** using **Microsoft Foundry**, **Microsoft Agent
> Framework**, **Foundry IQ**, **Foundry Toolbox** (web search +
> code-interpreter), **MCP servers** on **Azure Container Apps**, **Azure
> Cosmos DB**, and the **Foundry hosted-agents** runtime. The final modules
> layer on **quality evaluations**, **guardrails**, **red teaming**, and
> **end-to-end observability**.

You start with a runnable FastAPI chat UI that returns a stub response and,
exercise by exercise, replace the stub with real specialist agents —
testing in the browser as you go — until you have a Magentic orchestrator
coordinating four Foundry agents (one of them hosted on Foundry). The last
three modules add quality, safety and observability without disturbing the
working system.

The workshop is modelled on the
[Microsoft TechWorkshop L300 sample](https://github.com/microsoft/TechWorkshop-L300-AI-Apps-and-Agents)
and the
[Foundry hosted-agent demos](https://github.com/Azure-Samples/foundry-hosted-agentframework-demos).
Source files start as **scaffolds with TODOs**, every step shows the
solution behind an expandable block, and a complete reference implementation
lives under `solution/` mirroring `src/`.

---

## Scenario

You are building an internal assistant for **Pepsico** employees that
answers questions across three knowledge domains and synthesises a single
grounded reply.

| Domain      | Source of truth                                         | Tool surface                                |
| ----------- | ------------------------------------------------------- | ------------------------------------------- |
| HR          | Pepsico HR policies (Markdown)                          | **Foundry IQ** knowledge base               |
| Products    | Pepsico product catalog in **Azure Cosmos DB**          | **Products MCP Server** (Container App)     |
| Marketing   | Pepsico campaigns in Cosmos + briefs in Foundry IQ + live web | **Marketing MCP** + **Foundry IQ KB** + **Foundry Toolbox** (web search, code interpreter), all wrapped in a **Foundry-hosted** agent |

---

## Reference Architecture

```mermaid
flowchart LR
    U[User] -->|HTTP| W[FastAPI Chat App]
    W --> O[Magentic Orchestrator<br/>Microsoft Agent Framework]
    O --> HR[HR Agent<br/>Foundry Prompt Agent + Foundry IQ]
    O --> PR[Products Agent<br/>Foundry Prompt Agent + MCP Tool]
    O --> MK[Marketing Agent<br/>Foundry-HOSTED Agent<br/>Agent Framework]
    O --> RG[Response Generator<br/>Foundry Prompt Agent]
    HR  --> AIS[(Azure AI Search<br/>HR Foundry IQ KB)]
    PR  -->|MCP| PMCP[Products MCP Server<br/>Azure Container Apps]
    MK  -->|MCP| MMCP[Marketing MCP Server<br/>Azure Container Apps]
    MK  -->|MCP| MKB[(Marketing Foundry IQ KB)]
    MK  -->|MCP| TB[Foundry Toolbox<br/>web_search + code_interpreter]
    PMCP --> COS[(Cosmos DB<br/>products container)]
    MMCP --> COS2[(Cosmos DB<br/>marketing container)]
    W --> OBS[App Insights / OpenTelemetry]
    MK --> OBS
```

---

## Workshop Exercises

| #  | Exercise | Outcome |
| -- | -------- | ------- |
| 00 | [Setup & Verify Pre-Provisioned Resources](docs/00_setup/00_setup.md) | Local tooling installed; `.env` configured against your Foundry, Cosmos, Search, ACA. |
| 01 | [Scaffold the Chat App](docs/01_chat_app_scaffold/01_chat_app_scaffold.md) | Runnable FastAPI + HTML chat UI talking to a stub backend. |
| 02 | [Products MCP Server](docs/02_products_mcp_server/02_products_mcp_server.md) | FastMCP server seeded from Cosmos, running locally and on Container Apps. |
| 03 | [Products Foundry Agent + wire in](docs/03_products_foundry_agent/03_products_foundry_agent.md) | Products agent reachable via `AGENT_MODE=products`. |
| 04 | [Marketing MCP Server](docs/04_marketing_mcp_server/04_marketing_mcp_server.md) | Second FastMCP server for marketing campaigns. |
| 05 | [Foundry-hosted Marketing Agent (Foundry IQ + Web Tool)](docs/05_marketing_foundry_agent/05_marketing_foundry_agent.md) | Microsoft Agent Framework agent deployed via `azd ai agent up`, with Marketing MCP + Foundry IQ KB + Foundry Toolbox tools. |
| 06 | [HR Foundry IQ Agent + wire in](docs/06_hr_foundry_iq_agent/06_hr_foundry_iq_agent.md) | Knowledge-base-grounded HR agent. |
| 07 | [Magentic Orchestrator](docs/07_orchestrator_agent_framework/07_orchestrator_agent_framework.md) | `AGENT_MODE=orchestrator` routes/plans across all three specialists. |
| 08 | [Response Generator Agent](docs/08_response_generator/08_response_generator.md) | Final-answer synthesiser. |
| 09 | [Quality Evaluations](docs/09_evaluations/09_evaluations.md) | One-shot, scheduled, and continuous evals on the hosted Marketing agent. |
| 10 | [Guardrails & Red Teaming](docs/10_guardrails_red_teaming/10_guardrails_red_teaming.md) | Content-filter middleware + custom policies + automated red-team scan. |
| 11 | [End-to-End Observability](docs/11_observability/11_observability.md) | OpenTelemetry → App Insights and Foundry traces for chat app **and** hosted agent. |
| 12 | [Resource Cleanup](docs/12_cleanup/12_cleanup.md) | Remove container apps, hosted agents, KBs, eval schedules, connections you created. |

---

## Quick Start

> Full prerequisites are in [Exercise 00](docs/00_setup/00_setup.md). The minimum:

> No local Docker / container runtime is required — Container Apps deploys
> use ACR Tasks (cloud build) and the hosted Marketing agent is built by
> `azd ai agent up` against your Foundry account.

```powershell
# 1. Enter the repo
cd ai-agents-workshop

# 2. Create the venv and install the workshop package
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,framework,observability,mcp,evals,redteam]"

# 3. Configure the environment
Copy-Item .env.sample .env
# Edit .env and fill in values from your pre-provisioned Azure resources

# 4. Log in to Azure (DefaultAzureCredential is used everywhere)
az login
az account set --subscription "<your-subscription-id>"

# 5. Install the azd AI extension (needed from Exercise 05 onward)
azd extension install ai

# 6. Run the chat app right away (Exercise 01) — it will stub answers
uvicorn src.app.main:app --reload --port 8000
```

Open <http://127.0.0.1:8000>. As you finish each exercise, flip `AGENT_MODE`
in `.env` and restart uvicorn to wire in the new agent without changing the
frontend.

---

## Repository Layout

```
ai-agents-workshop/
├── docs/                          # Workshop content (Jekyll / just-the-docs)
│   ├── 00_setup/
│   ├── 01_chat_app_scaffold/
│   ├── 02_products_mcp_server/
│   ├── 03_products_foundry_agent/
│   ├── 04_marketing_mcp_server/
│   ├── 05_marketing_foundry_agent/      # Foundry-hosted agent (IQ + Web tool)
│   ├── 06_hr_foundry_iq_agent/
│   ├── 07_orchestrator_agent_framework/
│   ├── 08_response_generator/
│   ├── 09_evaluations/                  # Quality + scheduled + continuous evals
│   ├── 10_guardrails_red_teaming/       # Middleware + custom policies + red team
│   ├── 11_observability/
│   └── 12_cleanup/
├── src/                           # STARTER scaffolds — fill in as you go
│   ├── common/
│   ├── mcp_servers/products/
│   ├── mcp_servers/marketing/
│   ├── foundry_agents/
│   │   └── marketing_hosted/      # Microsoft Agent Framework hosted-agent code
│   ├── knowledge_seed/{hr,marketing}/
│   ├── evaluations/               # Scaffolds — see solution/evaluations/
│   ├── red_team/                  # Scaffolds — see solution/red_team/
│   └── orchestrator/
└── solution/                      # Full reference implementation
```

---

## Credits

Built on top of and inspired by:

* [Azure-Samples/foundry-hosted-agentframework-demos](https://github.com/Azure-Samples/foundry-hosted-agentframework-demos)
  — pattern for hosted agents, evaluations, guardrails, and red teaming.
* [microsoft/TechWorkshop-L300-AI-Apps-and-Agents](https://github.com/microsoft/TechWorkshop-L300-AI-Apps-and-Agents)
  — workshop format, exercise structure, and scaffold-to-solution pattern.
