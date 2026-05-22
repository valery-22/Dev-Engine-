# Dev-Engine — Autonomous SDLC Automation Platform

**A production-grade internal developer platform** that autonomously ingests GitHub repositories, detects issues, generates fixes, validates them in isolated Docker sandboxes, and opens Pull Requests.

Built with senior AI infrastructure engineering principles: **reliability-first**, observable, async-heavy, and using **only one LLM** throughout.

---

## 🎯 Core Goal

Dev-Engine acts as an autonomous AI pair-programmer that lives inside your engineering organization. It can take a broken repository and turn it into a working, validated Pull Request with zero human intervention after the initial trigger.

### Key Capabilities
- Repository ingestion & semantic indexing
- Build/runtime error detection
- Autonomous code fixing using a **single LLM**
- Isolated Docker validation sandbox
- Intelligent retry loop with execution history
- Automated Pull Request creation with full logs and explanations

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[GitHub Repository] --> B[Repository Ingestion Service]
    B --> C[File Parsing & Dependency Mapping]
    C --> D[Qdrant Vector DB + Metadata]
    
    E[Build / Runtime Error] --> F[Context Retrieval Engine]
    D --> F
    F --> G[Autonomous Fix Engine\n(LangGraph + Single LLM)]
    
    G --> H[Patch Application]
    H --> I[Validation Sandbox\nDocker Executor]
    
    I --> J{Validation Successful?}
    J -->|Yes| K[Pull Request Generator]
    J -->|No| L[Retry Evaluation Loop]
    L --> G
    
    K --> M[GitHub PR with Diff, Logs & Explanation]
    
    subgraph "Observability Layer"
        N[OpenTelemetry Tracing] 
        O[Structured JSON Logging]
        P[Metrics & Request Tracking]
    end
    
    N & O & P --> B & G & I & K
