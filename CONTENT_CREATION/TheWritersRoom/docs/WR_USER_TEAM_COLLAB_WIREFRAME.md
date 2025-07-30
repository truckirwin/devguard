# Writers Room User/Team/Collaboration Wireframe

This document provides a high-level wireframe flowchart for the Writers Room experience, showing the seamless flow for user onboarding, team creation, project collaboration, version control, and agent interaction. This is intended as a reference for UI/UX and backend development.

---

```mermaid
flowchart TD
  A1["User lands on WR app"] --> A2["Sign up or Log in (Google, Apple, Email)"] --> A3["Guided onboarding: profile, avatar, preferences"] --> A4["Dashboard: My Projects, My Teams"]
  A4 --> B1["Create Team"] --> B2["Invite Members (email, link)"] --> B3["Add AI Agents as Team Members"] --> B4["Set Roles: Owner, Editor, Commenter, Viewer, Agent"] --> B5["Team Dashboard: Members, Projects, Agents"]
  B5 --> C1["Create/Join Project"] --> C2["Open Screenplay Editor"] --> C3["Real-time Editing (Human + AI)"] --> C4["Live Presence: Avatars, Chat, Agent Bubbles"] --> C5["Comment, Suggest, Assign Tasks"] --> C6["Timeline: Save, Restore, Compare, Snapshots"]
  C6 --> D1["Auto-commit on Save/Action"] --> D2["Visual Timeline: Rewind, Restore, Compare"] --> D3["Alternate Versions (Drafts/Experiments)"] --> D4["Export: PDF, Final Draft, Fountain"]
  C4 --> E1["Chat with Agent"] --> E2["Agent Suggests/Edits/Comments"] --> E3["Accept/Reject/Modify Agent Suggestions"]
  E1 --> E4["Ask the Room for Multi-Agent Feedback"]
  A1 --> F1["No technical jargon"]
  A3 --> F2["Guided flows & tooltips"]
  A4 --> F3["Help: 'Show me how' videos"]
  A4 --> F4["Mobile/Desktop Responsive"]
```

---

**For Developer:**
- Use this wireframe to guide both UI/UX and backend API/service design.
- Each node can be mapped to a user story, UI component, or backend service endpoint.
- Update this document as flows evolve or new features are added. 