# 📖 Documentation Directory Index

Welcome to the **AI Career CoPilot** documentation directory. This folder houses deep-dive guides detailing the underlying technical designs, data schemas, background processes, and framework configurations of the platform.

---

## 📂 Documentation Manifest

| Document | Description | Key Sections |
| :--- | :--- | :--- |
| **[System Architecture](architecture.md)** | Overview of the multi-tier client-server structure and WebSocket routing. | • Client-Server Flow<br>• WebSocket Endpoint Mapping<br>• Sequence Diagrams (Discovery, Parser) |
| **[Data & AI Models](models_and_database.md)** | Details PostgreSQL schemas, Pydantic constraints, and AI models. | • DB Entity-Relationship Diagrams<br>• Pydantic v2 validation models<br>• LLM & Embedding configs (NVIDIA, Gemini) |
| **[Workflows & Agentic Systems](workflows_and_agents.md)** | Detailed agent triggers, math formulas, and Celery scheduling. | • Multi-agent state diagram (7 agents)<br>• Mathematical matching score formula<br>• Celery background tasks & Redis configurations |
| **[Tech Stack & Configurations](tech_stack.md)** | Standard listing of framework/package versions across frontend & backend. | • Next.js 16 Client dependencies<br>• FastAPI Backend requirement versions<br>• Docker compose services |

---

## 🛠️ Navigating the Docs

*   For **local setup, prerequisites, and developer instructions**, refer to the root [README.md](../README.md).
*   For **production deployment blueprints, environment config sheets, and memory optimization guidelines**, see the [Deployment Guide](../DEPLOYMENT.md).
*   For **system sequence diagrams and message payloads**, navigate to [architecture.md](architecture.md).
