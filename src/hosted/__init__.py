"""Foundry **hosted** agents — your own Agent Framework code, run by Foundry.

Unlike the declarative *Prompt Agents* under ``src/foundry_agents`` (model +
instructions + tools registered through ``create_version``), the modules in this
package are full Agent Framework ``Agent`` applications wrapped by
``agent_framework_foundry_hosting.ResponsesHostServer`` and packaged in a
container. Foundry runs the container and exposes it through the same Responses
API as every other agent.

See ``docs/11_hosted_agents`` for the concept, and
``inventory_hosted.py`` for the Zava Inventory hosted agent.
"""
