# Foundry-hosted Marketing agent

Reference implementation for Exercise 05 — a Microsoft Agent Framework agent
deployed to **Microsoft Foundry hosted agents** via `azd ai agent up`.

## Local run

```powershell
azd ai agent run
azd ai agent invoke --local "What is the ROI of CMP-2026-001?"
```

## Deploy

```powershell
azd ai agent up
azd ai agent show
azd ai agent monitor -f
```

## Tools wired

| Tool | Purpose |
| ---- | ------- |
| `marketing_mcp` MCP | Cosmos-backed campaign records (from Exercise 04) |
| `toolbox` MCP | Foundry built-ins (`web_search`, `code_interpreter`) |
| `marketing_kb` MCP | Foundry IQ KB over Pepsico marketing briefs |

See [docs/05_marketing_foundry_agent](../../../docs/05_marketing_foundry_agent/05_marketing_foundry_agent.md).
