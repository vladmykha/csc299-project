"""AI-inspired agents that reason over knowledge and tasks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .llm import LLMClient
from .models import KnowledgeEntry, Task
from .pkms import KnowledgeBase
from .tasks import TaskManager


@dataclass(slots=True)
class AgentResult:
    answer: str
    citations: list[str]
    knowledge: list[KnowledgeEntry]
    tasks: list[Task]
    suggested_actions: list[str]


class KnowledgeAgent:
    def __init__(self, knowledge_base: KnowledgeBase | None = None):
        self.knowledge_base = knowledge_base or KnowledgeBase()

    def retrieve(self, query: str, limit: int = 3) -> list[KnowledgeEntry]:
        return self.knowledge_base.search(query, limit=limit)


class TaskAgent:
    def __init__(self, task_manager: TaskManager | None = None):
        self.task_manager = task_manager or TaskManager()

    def retrieve(self, query: str, limit: int = 3) -> list[Task]:
        tasks = self.task_manager.list_tasks(limit=50)
        query_lower = query.lower()
        scored: list[tuple[float, Task]] = []
        for task in tasks:
            score = 0.0
            if query_lower in task.title.lower():
                score += 2.5
            if query_lower in task.description.lower():
                score += 1.5
            if task.status != "done":
                score += 1.0
            if score > 0:
                scored.append((score, task))
        if not scored:
            # fall back to TODO tasks
            scored = [(1.0, task) for task in tasks[:limit]]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [task for _, task in scored[:limit]]


class CampusConnectAgent:
    """Combines the PKMS, tasks, and LLM client to answer questions."""

    def __init__(
        self,
        *,
        knowledge_agent: KnowledgeAgent | None = None,
        task_agent: TaskAgent | None = None,
        llm_client: LLMClient | None = None,
    ):
        self.knowledge_agent = knowledge_agent or KnowledgeAgent()
        self.task_agent = task_agent or TaskAgent()
        self.llm_client = llm_client or LLMClient()

    def answer(self, prompt: str) -> AgentResult:
        knowledge_hits = self.knowledge_agent.retrieve(prompt, limit=3)
        task_hits = self.task_agent.retrieve(prompt, limit=3)
        context = self._build_context(prompt, knowledge_hits, task_hits)
        answer = self.llm_client.respond(*context)
        citations = [entry.id for entry in knowledge_hits] + [task.id for task in task_hits]
        suggested_actions = [
            f"Advance task '{task.title}' (status: {task.status})" for task in task_hits
        ]
        return AgentResult(
            answer=answer,
            citations=citations,
            knowledge=knowledge_hits,
            tasks=task_hits,
            suggested_actions=suggested_actions,
        )

    def _build_context(
        self,
        prompt: str,
        knowledge_hits: Sequence[KnowledgeEntry],
        task_hits: Sequence[Task],
    ) -> tuple[str, str]:
        system_prompt = (
            "You are a helpful academic success coach for DePaul University students. "
            "Use the provided knowledge entries and tasks to answer user questions. "
            "Cite concrete action items and stay concise."
        )
        knowledge_block = "\n".join(
            f"- [{entry.id}] {entry.title} ({', '.join(entry.tags) or 'untagged'}): {entry.content}"
            for entry in knowledge_hits
        ) or "No knowledge entries yet."
        task_block = "\n".join(
            f"- [{task.id}] {task.title} (status={task.status}, priority={task.priority}) — {task.description}"
            for task in task_hits
        ) or "No tasks found."
        user_prompt = (
            f"Question: {prompt}\n\n"
            f"Knowledge entries:\n{knowledge_block}\n\n"
            f"Tasks:\n{task_block}\n\n"
            "Respond with 2-3 sentences highlighting risks, upcoming deadlines, and a suggested next step."
        )
        return system_prompt, user_prompt
