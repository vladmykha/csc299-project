# Task 4 Plan – AI Agents & Chat Loop

## Objective
Demonstrate AI reasoning over the stored PKMS/task data via a chat interface, fulfilling the assignment requirement for AI agents interacting with the state.

## Inputs
- Task 3 CLI (for launching chat).
- OpenAI optional dependency and fallback requirement.

## Steps
1. Design agent abstractions (`KnowledgeAgent`, `TaskAgent`, `CampusConnectAgent`).
2. Implement retrieval logic scoring notes/tasks for a given prompt.
3. Build `LLMClient` that uses OpenAI Responses API when `OPENAI_API_KEY` is set, with deterministic fallback otherwise.
4. Create `ChatSession` to orchestrate prompts, display answers, and log transcripts.
5. Wire `campus-connect-cli chat` to instantiate the chat session.
6. Test both offline fallback and (if key provided) OpenAI responses.

## Deliverables
- `src/campus_connect_portal/agents.py`
- `src/campus_connect_portal/llm.py`
- `src/campus_connect_portal/chat.py`
- CLI `chat` subcommand (already present but now fully functional)

## Evidence
Running `campus-connect-cli seed --sample` followed by `campus-connect-cli chat` yields assistant responses that cite knowledge/task IDs, display suggested actions, and store transcripts in SQLite (verified with `storage.fetch_chat_history`).
