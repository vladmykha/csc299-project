# Task 4 – AI Agents & Chat Loop

Task 4 adds intelligence to the CLI by wiring Knowledge/Task agents, an LLM client with offline fallback, and a REPL (`campus-connect-cli chat`) that cites stored data—similar to the “AI agents” requirement on the assignment page.

## Goals
- Implement `KnowledgeAgent`, `TaskAgent`, and `CampusConnectAgent` that retrieve context and craft prompts.
- Provide an `LLMClient` that talks to OpenAI when available or summarizes locally when offline.
- Ship a `ChatSession` that logs transcripts, prints suggestions, and stores citations in SQLite.

## Key Artifacts

| Deliverable | Location | Notes |
| --- | --- | --- |
| Agents | `src/campus_connect_portal/agents.py` | Combines PKMS + task context, returns `AgentResult`. |
| LLM client | `src/campus_connect_portal/llm.py` | OpenAI Responses API + deterministic fallback summarizer. |
| Chat session | `src/campus_connect_portal/chat.py` | Interactive loop with logging + action suggestions. |
| CLI entry | `campus-connect-cli chat` | Launches chat session after DB has data. |

## Manual test
```bash
PYTHONPATH=src python3 -m campus_connect_portal.cli seed --sample
PYTHONPATH=src python3 -m campus_connect_portal.cli chat
# ask: "What should I follow up on before finals?"
```

Expected behavior (without `OPENAI_API_KEY`): assistant summarizes matching knowledge/tasks, prints “actions” and “citations,” and logs the conversation.

## Verification checklist
- [x] Offline fallback works when no API key is set.
- [x] Citations include both knowledge IDs and task IDs.
- [x] Chat transcripts are persisted in SQLite (`chat_messages` table).
