# Task 5 – Mobile Login Mock & Pulse-style Roadmap

Task 5 focuses on the “Pulse for Campus Connect” experience: design the mobile login/onboarding flow, explain how secure browser-based auth will work, and outline how the CLI foundation evolves into a mobile-first app.

## Goals
- Provide a UX mock for a Google/Pulse-style “Sign in with Campus Connect” flow.
- Document security expectations (embedded web modal, deep-link callback, session storage).
- Tie the mock to upcoming work: headless browser sync + mobile client.

## Key Artifacts

| Deliverable | Location | Notes |
| --- | --- | --- |
| Mobile login mock | `docs/MOBILE_LOGIN_MOCK.md` | Screens for welcome, auth choice, embedded login, and sync confirmation, plus error states. |
| README reference | `README.md` (Quick Start section) | Points reviewers to the mock and usage guide. |
| Future work outline | `docs/PROJECT_PLAN.md` (Milestones 4–5) | Describes browser automation + mobile client direction. |

## Talking points for demo
- Credentials never touch our servers; the app embeds the official Campus Connect login page and listens for a redirect.
- Once authenticated, the same sync engine that powers the CLI will refresh grades, financial aid, schedules, and advisor notes.
- Manual JSON import remains available for students who prefer local/offline use.

## Verification checklist
- [x] Mobile mock covers at least four screens plus failure states.
- [x] README links to the mock so graders can find it quickly.
- [x] Plan describes how mobile + automation fit into the existing architecture.
