# 🗄️ Models & Database Schema

This document details the relational database schema, data validation contracts, and AI model configurations that form the backbone of the **AI Career CoPilot** platform.

---

## 📊 Relational Database Schema (SQLAlchemy / PostgreSQL)

All relational models are defined in `backend/app/models.py`.

```mermaid
erDiagram
    users ||--o{ profiles : "has"
    users ||--o{ applications : "manages"
    jobs ||--o{ contacts : "has"
    jobs ||--o{ applications : "tracks"
    contacts ||--o{ messages : "has"

    users {
        UUID id PK
        String clerk_id UK
        String name
        String email UK
        DateTime created_at
        DateTime updated_at
    }

    profiles {
        UUID id PK
        UUID user_id FK
        Integer version
        Text raw_text
        JSON skills
        JSON projects
        JSON education
        JSON experience
        JSON certifications
        String resume_url
        String embedding_id
        Boolean is_active
        DateTime created_at
    }

    jobs {
        UUID id PK
        String title
        String company
        Text description
        JSON skills_required
        String location
        Boolean remote
        Integer salary_min
        Integer salary_max
        Integer experience_years_min
        Integer experience_years_max
        String source
        String source_url
        String source_hash UK
        Float match_score
        JSON match_explanation
        String status
        Date posted_date
        DateTime discovered_at
        String embedding_id
    }

    companies {
        UUID id PK
        String name UK
        String domain
        Text overview
        JSON tech_stack
        String funding_stage
        String team_size
        JSON recent_news
        Text ai_focus
        Text why_fit
        DateTime last_researched_at
    }

    contacts {
        UUID id PK
        UUID job_id FK
        String name
        String title
        String company
        String linkedin_url
        String email
        Float email_confidence
        Integer connection_degree
        String source
        String status
        Text notes
        DateTime created_at
    }

    messages {
        UUID id PK
        UUID contact_id FK
        UUID job_id FK
        String type
        Text draft
        Text final_text
        DateTime sent_at
        DateTime replied_at
        String status
        DateTime created_at
    }

    applications {
        UUID id PK
        UUID user_id FK
        UUID job_id FK
        Integer profile_version
        String status
        Date applied_date
        String platform
        JSON interview_rounds
        JSON offer_details
        Text notes
        DateTime updated_at
    }
```

### Table Details

#### 1. `users`
Stores user authentication profile data synchronizing with Clerk.
*   `id`: Primary key (UUID).
*   `clerk_id`: Unique Clerk identifier (Indexed).
*   `name`: User's display name.
*   `email`: User's verified email address (Indexed).

#### 2. `profiles`
Parsed resumes mapped to specific versions.
*   `user_id`: Foreign key referencing `users.id`.
*   `skills`: Map of skills categorized into `languages`, `frameworks`, and `tools`.
*   `projects`: List of project objects with name, tech stack, description, and impact metrics.
*   `is_active`: Boolean flag indicating if this is the active matching profile.

#### 3. `jobs`
Aggregated job postings discovered by scraper workers.
*   `source_hash`: SHA256 of `company_name + job_title + location` (Unique, Indexed).
*   `match_score`: Cosine similarity & overlap percentage score (0.0 to 100.0) (Indexed).
*   `status`: Discovery pipeline stage (`discovered`, `saved`, `applied`, `rejected`).

#### 4. `contacts`
Alumni or recruiter contacts found for a job.
*   `email_confidence`: Score from 0.0 to 1.0 indicating guessed email validity.
*   `status`: Outreach status (`discovered`, `pending_outreach`, `contacted`).

#### 5. `messages`
Generated LinkedIn & email outreach text.
*   `type`: Message classification (`linkedin_referral`, `cold_email`, `follow_up`).
*   `status`: Draft status (`draft`, `sent`, `replied`).

#### 6. `applications`
Active job tracking workflow entries.
*   `status`: Kanban pipeline step (`saved`, `applied`, `interviewing`, `offered`, `rejected`).
*   `interview_rounds`: JSON array tracking dates, interviewers, prep checklists, and results per round.

---

## 🔒 Data Validation (Pydantic v2)

API payload schema contracts are defined in `backend/app/schemas.py`.

*   **Pydantic strict typing**: Validates field definitions such as `EmailStr` for user creation and `UUID` identifiers.
*   **Attributes Serialization (`from_attributes = True`)**: Configured on responses to convert SQLAlchemy models into JSON payloads automatically.
*   **JSON Structures**: Structured maps (e.g. `skills: Optional[Dict[str, List[str]]]` and lists of key-value pairs) enforce field-level constraints.

---

## 🧠 AI / ML Models & Vector Databases

### 1. Large Language Models (LLMs)

The platform abstracts LLM interactions in `backend/app/services/llm.py`:

*   **Primary LLM: NVIDIA NIM (Llama 3.1 70B Instruct)**
    *   **Purpose**: Heavy-duty processing, including resume PDF schema extraction (generating structured JSON matching target profiles) and writing hyper-personalized outreach drafts.
    *   **Deployment**: Hosted as an optimized microservice (NVIDIA NIM inference endpoint).
*   **Fallback LLM: Google Gemini 2.0 Flash**
    *   **Purpose**: Lightweight structural updates, formatting, fast summary extraction, and serving as a fallback model during high latency or rate limits.
    *   **SDK**: `google-generativeai`

### 2. Embeddings & Semantic Similarity

*   **Model: BGE-M3 (via Sentence Transformers)**
    *   **Dimension**: 1024-dimensional dense vectors.
    *   **Purpose**: Generates high-quality semantic representations of job descriptions and structured resume components (such as project summaries and professional descriptions).
    *   **Local Execution**: Loaded into PyTorch context on the celery workers or backend APIs.

### 3. Vector Indexing Database

*   **ChromaDB**:
    *   **Storage**: Local persistent vector index database (`chroma_db` directory).
    *   **Collections**:
        *   `resumes`: Embeddings of resume segments and project accomplishments.
        *   `jobs`: Embeddings of scraped job description files.
    *   **Workflow**: When the matching service triggers, it pulls nearest neighbors for target job descriptions against the active profile sections using Cosine Similarity checks.
