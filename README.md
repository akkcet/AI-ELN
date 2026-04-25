# 🧪 AI‑Native Electronic Lab Notebook (ELN)

A **modern, workflow‑first Electronic Lab Notebook (ELN)** designed to replace traditional ELN systems and optionally enhance them with **governed, human‑in‑the‑loop AI capabilities**.

This platform delivers all the core functionality of a conventional ELN **out of the box**, while providing a safe and extensible foundation for organizations that want to gradually adopt AI—**without sacrificing control, compliance, or auditability**.

---

##  Purpose

Most ELN systems successfully digitize lab notebooks, but they struggle to adapt to modern R&D environments that require:

- Clear workflows
- Dynamic taxonomies
- Strong governance
- Rapid administrative changes
- Better discoverability of information

This project re‑imagines the ELN as a **workflow‑driven, admin‑controlled system**, with AI as an **optional, additive layer**—not a dependency.

---

##  A Complete Replacement for Traditional ELNs

This system is a **fully functional ELN even if all AI features are disabled**.

### Core ELN Capabilities (No AI Required)

- Structured experiment records
- Section‑based experiment composition
- Project management
- Admin‑managed dropdowns and lookups
- File attachments (PDFs, images, Excel files, etc.)
- Versioned saves
- Review and approval workflows
- Full audit trail
- Traceable state transitions
- SQLite / SQLAlchemy persistence

✅ You can deploy and use this platform today as a **traditional ELN replacement**.

---

##  What Makes This ELN Different

### 1️⃣ Workflow‑First by Design

Instead of treating workflows as an afterthought, this system makes them explicit:
- Every state is visible  
- Every transition is deterministic  
- Every action is traceable  
- No silent changes  

This provides **stronger governance than most legacy ELNs**.

---

### 2️⃣ Admin‑Driven Configuration

All controlled vocabularies are managed through a dedicated Admin UI:

- Projects
- Categories
- Lookups
- Dropdown values

* No hard‑coded lists  
* No redeployments for taxonomy changes  
* Fully auditable configuration changes  

---

### 3️⃣ Clear Separation of Concerns

The architecture enforces strict separation between:

- UI (Streamlit)
- API (FastAPI)
- Business logic (services & agents)
- Workflow execution (state machine)
- Persistence (SQLAlchemy / SQLite)

This makes the system easier to maintain, validate, and extend.

---

## 🤖 Optional AI Layer (Governed & Safe)

AI is **not required** to use this ELN.

When enabled, AI is used **only where it is safe and valuable**, such as:

- Navigating existing information
- Reducing administrative friction
- Improving usability

AI is **never used** to:

- Design experiments
- Interpret scientific results
- Make autonomous changes
- Bypass approvals

---

### AI‑Assisted Capabilities (Optional)

- Natural‑language Q&A over existing experiments
- Knowledgebase search using retrieval‑augmented generation (RAG)
- Chat‑based creation of administrative requests
- AI‑assisted workflow orchestration

* All AI actions are mediated by approval workflows  
* No autonomous execution  
* No uncontrolled side effects  

---

##  Multi‑Agent Architecture (When AI Is Enabled)

When AI is enabled, the platform runs a governed multi‑agent system:

### Agents

- **QnA Agent**
  - Read‑only access to experiments and documents
  - Answers questions using existing data only

- **Admin Request Agent**
  - Converts natural‑language requests into formal workflow requests
  - Does not modify data directly

- **Workflow Agent**
  - Manages approvals and execution
  - Enforces state transitions

### Orchestrator

A central orchestrator routes each request to the appropriate agent, ensuring:

- Correct intent handling
- Safety boundaries
- Human‑in‑the‑loop governance

---

##  Approval & Execution Governance

Administrative actions follow a strict lifecycle:
**NewRequest → Approved → Executed → Complete**
- Requests are logged
- Approvers must explicitly approve changes
- Execution happens in a controlled background process
- All actions are auditable

This makes governance **explicit, inspectable, and robust**.

---


## Compliance‑Ready by Design
Even with AI enabled:

All changes are auditable
Approvals are mandatory
AI does not act autonomously
Human accountability is preserved

This makes the platform well‑suited for regulated R&D environments.

