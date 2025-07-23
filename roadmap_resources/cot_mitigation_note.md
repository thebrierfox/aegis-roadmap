## Chain-of-Thought Mitigation Note

This note explains the guidelines for handling chain-of-thought (CoT) reasoning within AEGIS Master Roadmap tasks and deck usage. The intention is to preserve agent reasoning while avoiding disclosing raw internal reasoning that could reveal sensitive heuristics or violate privacy policies.

### Guidelines

- **Summarise reasoning**: When capturing insights or decisions, summarise the high-level rationale rather than copying the full step-by-step chain-of-thought. Use bullet points or succinct statements that capture the essence of your reasoning.

- **Protect internal states**: Internal reasoning is considered private; do not commit raw CoT logs to the repository or share them with external stakeholders. Instead, summarise them into actionable insights.

- **Limit retention**: Do not store full chains-of-thought in persistent storage. Only store summarised versions that capture final decisions, key trade-offs, and rationales.

- **Reference context**: When summarising reasoning, provide citation or context pointers (e.g., memory citations) to support future auditing without revealing the full chain-of-thought.

- **Compliance**: Follow OpenAI’s safe browsing and privacy policies when handling sensitive information. Avoid storing or sharing user-specific or sensitive data in summarised notes.

### Purpose

By following these mitigation guidelines, the roadmap decks remain transparent and informative while respecting user privacy and system policies. This supports continuous improvement and responsible AI operations.
