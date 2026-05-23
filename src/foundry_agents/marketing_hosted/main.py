"""Foundry-hosted Marketing agent — TODO: implement.

See docs/05_marketing_foundry_agent/05_02_build_hosted_marketing_agent.md.

Steps:
1. Build a ChainedTokenCredential (ManagedIdentity + AzureDeveloperCli).
2. Construct three MCPStreamableHTTPTool tools:
   - Marketing MCP (MARKETING_MCP_URL)
   - Foundry Toolbox (web_search + code_interpreter)
   - Marketing Foundry IQ KB (knowledge_base_retrieve)
3. Build a FoundryChatClient and Agent.
4. Hand it to ResponsesHostServer(agent).run().

Reference: solution/foundry_agents/marketing_hosted/main.py
"""
from __future__ import annotations

import logging

logger = logging.getLogger("marketing-hosted-agent")


def main() -> None:
    raise NotImplementedError("Implement per docs/05_marketing_foundry_agent/05_02_build_hosted_marketing_agent.md")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
