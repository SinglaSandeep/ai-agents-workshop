---
title: Setup
layout: default
nav_order: 1
parent: Workshop Guide
---

# Setup

## Goal

Prepare a local Python environment and confirm the workshop app can run from the command line.

## Prerequisites

- Python 3.11 or later
- PowerShell or another terminal
- Visual Studio Code

## Steps

1. Open a terminal in the project folder.

```bash
cd ai-agents-workshop
```

2. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install the workshop package.

```bash
python -m pip install -e .
```

4. Confirm the CLI is available.

```bash
python -m app.cli --help
```

## Success Criteria

- The virtual environment is active.
- `python -m app.cli --help` prints command options.
- You can explain that the first exercises run locally with markdown knowledge files.

## Running Version

At the end of setup, run:

```bash
python -m app.cli --query "What is the PTO policy?"
```

Expected result: the app routes to the HR agent and returns an answer from `app/knowledge/hr.md`.
