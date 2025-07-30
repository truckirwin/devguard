# Writers Room Agent Chat Wireframe

This document provides a detailed wireframe flowchart for the agent chat experience in Writers Room, showing the flow for user-agent interaction, agent suggestions, multi-agent feedback, and chat management. Use this as a reference for UI/UX and backend development.

---

```mermaid
flowchart TD
  AC1["User opens Screenplay Editor"] --> AC2["Agent Chat Panel (Sidebar/Webview)"]
  AC2 --> AC3["Select Agent (Script Doctor, Sorkin, etc.)"]
  AC3 --> AC4["Type message or select quick prompt"]
  AC4 --> AC5["Send message to Agent"]
  AC5 --> AC6["Agent processes request (AWS Bedrock)"]
  AC6 --> AC7["Agent responds in chat (suggestion, feedback, or edit)"]
  AC7 --> AC8["User can:"]
  AC8 --> AC9["Accept Suggestion (applies to script)"]
  AC8 --> AC10["Reject Suggestion (dismiss)"]
  AC8 --> AC11["Modify Suggestion (edit before applying)"]
  AC8 --> AC12["Ask Follow-up or Clarification"]
  AC7 --> AC13["Agent can:"]
  AC13 --> AC14["Suggest Inline Edit"]
  AC13 --> AC15["Add Comment/Annotation"]
  AC13 --> AC16["Request More Context"]
  AC2 --> AC17["Switch to Another Agent"]
  AC2 --> AC18["Ask the Room (multi-agent feedback)"]
  AC18 --> AC19["All agents respond (debate, consensus, or multiple suggestions)"]
  AC19 --> AC8
  AC1 --> AC20["Agent avatars, bios, and personalities visible"]
  AC2 --> AC21["Chat history and search"]
  AC2 --> AC22["Pin important agent responses"]
  AC2 --> AC23["Export chat to project notes"]
```

---

**For Developer:**
- Use this wireframe to guide the agent chat UI/UX and backend API/service design.
- Each node can be mapped to a user story, UI component, or backend service endpoint.
- Update this document as flows evolve or new features are added. 