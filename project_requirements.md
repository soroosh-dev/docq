# Project Requirements – Docq: Chat With Your Documents

## 1. Product Overview

**Docq** is an enterprise-grade platform that enables users to interact with documents through natural language queries. By uploading files (e.g., PDFs, DOCXs), users can “chat” with the content to quickly find and reference information. The platform is designed for organizations requiring robust access control, document referencing, and centralized administration.

---

## 2. Core Value Proposition

- Transform static documents into interactive knowledge bases.
- Enable natural language querying, searching, and referencing within uploaded documents.
- Provide granular control over content access with document-level permissions.
- Offer a centralized admin panel for streamlined file management and user permissions.

---

## 3. User Roles

### Admin
- Uploads and manages documents.
- Assigns access levels.
- Manages user accounts and permissions.

### Standard User
- Interacts with approved documents via chat functionality.

### Viewer (Optional)
- Read-only access with no chat permissions.

---

## 4. Key Features

### 4.1. Document Upload & Management
- Supports PDF, DOCX, TXT, and HTML formats.
- Drag-and-drop or form-based upload via the admin panel.
- Automatic text extraction and chunking for context-aware queries.
- Custom metadata fields: title, category, tags, visibility.

### 4.2. Chat With Your Documents
- Natural language processing using OpenAI or similar LLMs.
- Contextual conversation with chat history per document.
- Responses include inline references (e.g., “As stated on Page 4...”).
- Toggle between Chat Mode and Search Mode.

### 4.3. Access Levels
- **Private**: Visible only to uploader/admin.
- **Team Only**: Shared within specific group.
- **Organization-wide**: Accessible to all users.
- **Public (Optional)**: External knowledge base.

### 4.4. Admin Dashboard
- Upload, update, and delete documents.
- Manage user roles and permissions.
- View analytics (e.g., queries per document, active users).
- Tagging and categorization tools.

### 4.5. Document Referencing
- Users can cite specific sections in queries.
- Inline citations with page or paragraph references.
- Clickable links in responses to relevant document snippets.

---

## 5. Architecture & Stack Recommendations

| Component        | Suggested Stack                                |Chosen Stack                |
|------------------|------------------------------------------------|----------------------------|
| Frontend         | React (Next.js) + Tailwind CSS                 | React (Next.js) + Tailwind CSS |
| Backend          | Node.js (Express/NestJS)                       | Django + Django rest framework |
| Auth             | Auth0 / Firebase Auth / Supabase               | Knockknock app |
| Database         | PostgreSQL (with Prisma)                       | Postgres + chroma |
| Document Parsing | PDF.js, docx-parser, LangChain, LlamaIndex     | - |
| AI Chat Layer    | OpenAI API or open-source LLM                  | OpenAI API|
| Storage          | AWS S3 or Firebase Storage                     | file storage |
| Hosting          | Vercel / Render / Heroku                       | Runflare |

---

## 6. Security & Compliance

- Role-based Access Control (RBAC).
- Encryption at rest and in transit.
- Audit logging for uploads and user queries.
- Optional SSO (SAML/OAuth) integration.

---

## 7. MVP Scope

| Feature                    | Included in MVP? |
|----------------------------|------------------|
| Document upload (PDF, DOCX)| ✅               |
| Admin panel                | ✅               |
| Chat interface             | ✅               |
| Access level system        | ✅               |
| Basic document referencing | ✅               |
| User management            | ✅               |
| Search mode                | ❌ (Post-MVP)    |
| Version control            | ❌ (Post-MVP)    |

---

## 8. Success Metrics

- Time to first meaningful chat after upload.
- Monthly Active Users (MAU).
- Average queries per document.
- CSAT/NPS survey scores.
- Reduced time spent searching static documents.

---

**Note**: Features like Search Mode, Version Control, and Extended Integrations will be considered post-MVP based on user feedback and roadmap priorities.
