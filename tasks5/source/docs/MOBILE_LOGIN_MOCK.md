# Mobile Login Experience — Campus Connect Assistant

This mock illustrates how the planned mobile client will guide students through a “Sign in with Campus Connect” experience, mirroring familiar flows like Pulse or Google OAuth popups. The goal is to keep credentials inside DePaul’s official login page while our app simply brokers the session token.

## Screen 1 — Welcome

```
+----------------------------------------------------+
|  CAMPUS CONNECT PORTAL                             |
|                                                    |
|  Stay on top of grades, registration, and aid.     |
|                                                    |
|  [ Get Started ]                                   |
+----------------------------------------------------+
```

- **Primary action**: “Get Started” pushes to a dedicated login screen.
- Secondary text explains that the app reads your data directly from Campus Connect and stores it locally.

## Screen 2 — Choose authentication

```
+----------------------------------------------------+
|  Sign in                                           |
|                                                    |
|  Connect your Campus Connect account to sync       |
|  grades, schedules, and financial aid updates.     |
|                                                    |
|  (i) Your credentials stay on the official site.   |
|                                                    |
|  [ Use DePaul Login ]                              |
|        icon: campus-connect-logo                   |
|                                                    |
|  (Optional)                                        |
|  [ Manual Import ]                                 |
+----------------------------------------------------+
```

- “Manual Import” keeps parity with the current JSON/CLI workflow.
- The info blurb reassures users about credential handling.

## Screen 3 — In-app web modal (Campus Connect SSO)

```
+----------------------------------------------------+
|  Campus Connect (embedded browser)                 |
|  ------------------------------------------------  |
|  | Username: [__________________________]       |  |
|  | Password: [__________________________]       |  |
|  |                                              |  |
|  | [ Sign In ]                                  |  |
|  ------------------------------------------------  |
|                                                    |
|  This secure modal is the official DePaul login.   |
|  We never store your password.                     |
+----------------------------------------------------+
```

- Implemented with an `SFSafariViewController` / `WebView` style component on mobile so the official Campus Connect page handles credentials.
- When sign-in succeeds, the web view redirects to a deep link our app listens for (e.g., `campusconnect://auth/callback?session=...`).

## Screen 4 — Permissions + sync confirmation

```
+----------------------------------------------------+
|  Sync your data                                    |
|                                                    |
|  ✅ Grades                                         |
|  ✅ Financial Aid                                  |
|  ✅ Class Schedule                                 |
|  ✅ Advisor Notes                                  |
|                                                    |
|  Data is stored locally and can be wiped anytime.  |
|                                                    |
|  [ Start Sync ]                                    |
+----------------------------------------------------+
```

- Tapping “Start Sync” kicks off the headless browser/Playwright job on the backend service (or local agent) using the authenticated session.
- This screen doubles as a place to explain how often sync happens (e.g., every 6 hours, manual refresh available).

## Failure / Retry states

- **Invalid credentials**: web modal shows the Campus Connect error banner; we surface “Need help?” linking to DePaul’s password reset.
- **Timeout or MFA required**: present a sheet explaining the app can’t bypass MFA; user can re-open the modal or switch to manual import.
- **Network offline**: show “Connect to the internet to finish logging in.”

## Implementation notes

1. **Security**: Credentials never hit our servers. The web modal loads `https://campusconnect.depaul.edu/` directly; we only watch for the final redirect URL.
2. **Session token storage**: once authenticated, store an encrypted session cookie in the mobile secure enclave / keychain, scoped to the sync service.
3. **CLI parity**: the desktop CLI keeps a `login` command that opens a system browser and listens on `localhost` for the same callback, so both mobile and desktop share the OAuth-style flow.
4. **Next steps**: once backend automation is ready, this mock will inform the actual UI build (e.g., React Native screens + Playwright-based sync engine).
