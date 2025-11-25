"""Terminal chat interface for the Campus Connect assistant."""

from __future__ import annotations

import textwrap
from uuid import uuid4

from .agents import AgentResult, CampusConnectAgent, KnowledgeAgent, TaskAgent
from .llm import LLMClient
from .pkms import KnowledgeBase
from .storage import Storage
from .tasks import TaskManager


class ChatSession:
    def __init__(
        self,
        *,
        agent: CampusConnectAgent | None = None,
        storage: Storage | None = None,
    ):
        storage = storage or Storage()
        knowledge_agent = KnowledgeAgent(knowledge_base=KnowledgeBase(storage=storage))
        task_agent = TaskAgent(task_manager=TaskManager(storage=storage))
        self.agent = agent or CampusConnectAgent(
            knowledge_agent=knowledge_agent,
            task_agent=task_agent,
            llm_client=LLMClient(),
        )
        self.storage = storage
        self.session_id = str(uuid4())

    def interact(self) -> None:
        print("Campus Connect chat ready. Type 'quit' to exit.")
        while True:
            try:
                prompt = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                break
            if prompt.lower() in {"quit", "exit"}:
                print("Goodbye!")
                break
            if not prompt:
                continue
            self._log("user", prompt)
            result = self.agent.answer(prompt)
            self._display(result)
            self._log("assistant", result.answer, result.citations)

    def _display(self, result: AgentResult) -> None:
        wrapped = textwrap.fill(result.answer, width=88)
        print(f"\nassistant> {wrapped}")
        if result.suggested_actions:
            print("actions:")
            for action in result.suggested_actions:
                print(f"  - {action}")
        if result.citations:
            print(f"citations: {', '.join(result.citations)}")
        print("")

    def _log(self, role: str, content: str, citations: list[str] | None = None) -> None:
        citations = citations or []
        from .models import ChatMessage  # local import to avoid cycle

        message = ChatMessage(
            session_id=self.session_id,
            role=role,
            content=content,
            citations=citations,
        )
        self.storage.insert_chat_message(message.to_row())
