# PathLog: Encrypted Memory Kernel for Multi-Agent Intelligence

## 1. Purpose
PathLog is the personal intelligence archive for the Value Adders ecosystem. It captures, encrypts, and organises a citizen's interactions with AI services so they can recall context, track growth, and control their data. The system exists to:
- Provide a universal memory layer across agents such as ChatGPT, Claude, custom GPTs, trading bots, and internal Value Adders assistants.
- Preserve intellectual trace with end-to-end encryption so only the citizen can decrypt their history.
- Offer tools that map personal evolution, surface insights, and enable context-aware recall inside civic and commercial experiences.

## 2. Experience Narrative
1. A citizen links the PathLog browser extension and mobile SDK to authorised AI channels.
2. Every AI conversation (prompt + response + metadata) streams into an encrypted vault in the citizen's control.
3. The Path Engine tags and clusters entries, building timelines of breakthroughs, blockers, topics, and emotional signals.
4. The Recall Interface (timeline UI, semantic search, VANTORIA voice assistant) lets the citizen ask, "What was my Claude insight on May 3rd?" and receive decrypted context on demand.
5. Agents in the Value Adders network request context via consented APIs, powering continuity across missions, rituals, and commerce.

## 3. Core Capabilities
### 3.1 Encryption Engine
- AES-256-GCM per-record encryption using rotating keys derived from a PQ-resistant root key.
- Key custody options: biometric unlock, seed phrase, and hardware key vault.
- Zero-knowledge design: PathLog services never store plain text or receive decryption keys.
- Tamper-evident ledger of key rotations and access events.

### 3.2 AI Sync Hooks
- Browser extension intercepts DOM events for ChatGPT, Claude, Gemini, Notion AI, Perplexity, and selected Discord/Slack bots.
- API adapters capture structured payloads from Value Adders internal agents and external AI APIs.
- Stream processor normalises content into a shared JSON schema (channel, role, content, tags, source URL, sentiment, embedding vector).

### 3.3 Path Engine (Intelligence Layer)
- NLP pipelines generate embeddings, emotion scores, and topic tags.
- Conversation linker groups threads across platforms.
- Milestone detector surfaces breakthroughs, decisions, and commitments for later follow-up.
- Optional personalised models run locally in the citizen's vault for Ancestral Voice and Path guidance.

### 3.4 Recall Interface
- Encrypted timeline web app built with Next.js + Supabase Row Level Security.
- VANTORIA voice skill enabling natural language recall with on-device decryption.
- Smart cues delivered to AddValue App rituals (Activation Day, Weekly Wave) using summarised insights.

### 3.5 Identity Over Time
- Dynamic Persona Graph showing evolution of goals, skills, and confidence.
- Reflection prompts triggered by streaks, breakthroughs, or detected friction.
- Export packages (PDF, JSON, secure share links) so citizens can collaborate or migrate.

## 4. Data Architecture
- **Capture Layer:** Extension/SDK publishes events to an encrypted ingestion API (HTTPS + mTLS).
- **Ingestion Queue:** Kafka or NATS streams events into worker pods; all payloads encrypted client-side.
- **Vault Storage:** Encrypted blobs stored in S3-compatible object storage with per-user buckets and client-managed keys via AWS KMS External Key Store or Hashicorp Vault.
- **Index Store:** PostgreSQL + pgvector storing metadata and embeddings only (no plain content).
- **Processing Workers:** Serverless functions decrypt within secure enclave (TEE / Nitro) when the citizen authorises processing jobs.
- **Access Gateway:** GraphQL API enforcing consent tokens, rate limiting, and audit logging.

## 5. Security & Compliance
- SOC2-aligned controls; automated audit trails for key usage, access grants, and processing jobs.
- Compliance with GDPR/POPIA data rights; self-serve deletion + export.
- Differential privacy on aggregate analytics; zero data sharing without explicit consent.
- Incident response playbook with 1-hour detection SLAs and citizen notification workflow.

## 6. Interactions with Value Adders Agents
- Orchestrator requests PathLog summaries via secure webhook; summary generation runs in citizen-controlled enclave.
- Developer and Technical Architect agents own integration backlogs for extension + API connectors.
- Legal/Ethics agent enforces encryption policies, retention rules, and cross-border data requirements.
- Spiritual Alignment agent ensures reflections and prompts reinforce the Living Constitution.

## 7. Implementation Roadmap
1. **MVP (Weeks 1-4)**
   - Ship Chrome extension capturing ChatGPT + Claude sessions.
   - Deliver local encrypted vault (SQLite + age/Libsodium) with manual export.
   - Build basic timeline UI and search over embeddings.
2. **Beta (Weeks 5-10)**
   - Add cloud vault with user-managed keys (BYOK) and secure device sync.
   - Integrate AddValue App rituals with PathLog insights.
   - Release first VANTORIA voice recall prototype.
3. **Launch (Weeks 11-16)**
   - Harden TEE processing, multi-agent API, and mobile SDK.
   - Achieve SOC2 Type I readiness checklist.
   - Run closed pilot with 100 citizens and gather retention metrics.
4. **Scale (Post-launch)**
   - Introduce federated learning for personalised models.
   - Expand connectors (Perplexity, Gemini, enterprise bots).
   - Offer paid tiers: Guardian-grade compliance, collaborative vaults for teams.

## 8. Success Metrics
- Vault activation rate (citizens installing extension + unlocking).
- Daily synced interactions per citizen and cross-agent recall usage.
- Time-to-recall (avg seconds from query to decrypted insight).
- Privacy posture: zero unauthorised access events, key rotation completion rate.

## 9. Open Questions
- Preferred custody provider for hardware-backed keys (YubiKey vs. Ledger vs. custom card).
- Pricing and tier strategy aligning with Guardian and Valutoria bundles.
- Data residency requirements for pan-African rollout and sovereign cloud options.

## 10. Next Actions
- Technical Architect: finalise secure enclave vendor evaluation and queue design.
- Developer: prototype Chrome capture + local vault encryption pipeline.
- Product Manager: validate reflection prompts and persona graph UX with pilot citizens.
- Legal/Ethics: draft consent flow copy and retention policies for encrypted archives.



## 11. Prototype Implementation Notes
- Source: `pathlog/` package ships a FastAPI backend (`uvicorn pathlog.api:app`).
- Quickstart CLI (`python -m pathlog.quickstart`) provisions a vault, connects tools, captures events, rotates keys, and exports a bundle for backup.
- Data at rest lives under `pathlog_data/` with encrypted payloads (Fernet/AES-256-GCM) and downloadable key files per user.
- Dependencies: `fastapi`, `uvicorn`, `cryptography`, and `pydantic` (install via `pip install fastapi uvicorn cryptography pydantic`).


## 12. Chrome Bridge Prototype
- `pathlog/browser_extension/` ships a Manifest V3 Chrome extension that forwards highlighted chat text to the PathLog `/capture` endpoint.
- Users configure API base URL, user ID, and optional passphrase via the extension options page; the default target is the local FastAPI instance (`http://localhost:8002`).
- Right-click context menu "Send selection to PathLog" (or Alt+Shift+L hotkey) posts prompts/responses with page metadata, providing a lightweight capture flow ahead of native platform integrations.
- Packaging instructions (`pathlog/browser_extension/README.md`) cover loading the unpacked build and submitting a zipped artifact to the Chrome Web Store.


