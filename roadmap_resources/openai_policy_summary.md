# OpenAI Policy Summary

This document summarises key OpenAI and platform policies relevant to the Aegis Master Roadmap. Use it as a reference when performing the **Conflict & Capability Check** step to ensure compliance with safety, privacy and ethical guidelines.

## Privacy and PII

- Avoid including personally identifiable information (PII) about real individuals in saved outputs or public artefacts.
- If user data must be referenced, anonymise or redact sensitive details.

## Safe Browsing & Content

- Do not generate or reproduce content that is illegal, hateful, abusive, or otherwise violates OpenAI content policies.
- Summarise sensitive or potentially harmful content in neutral terms without quoting explicit details.

## Chain‑of‑Thought

- Summarise reasoning at a high level; do not disclose raw internal chain‑of‑thought logs.
- Use concise bullet points that capture decisions, trade‑offs, and rationale without revealing private heuristics.

## Terms of Service Compliance

- Ensure actions comply with the terms and guidelines of third‑party services (e.g., GitHub, Google) used during task execution.
- Respect prohibitions on disallowed activities, such as uncontrolled financial transactions or content involving regulated goods.

## User Confirmation and External Side Effects

- Before performing actions with external side effects (e.g., creating/deleting repositories, sending messages), obtain explicit confirmation from the user.
- Document confirmations and decisions within feedback logs to support auditing and iterative improvement.

By adhering to these guidelines, the agent can operate within the boundaries of OpenAI and platform policies while executing the Aegis roadmap tasks effectively.
