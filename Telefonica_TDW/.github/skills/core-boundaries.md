# Core Boundaries & Security Rules (Never Violate)
- **Credentials:** NEVER include hardcoded credentials or tokens in plain text.
- **Security:** NEVER expose transactional endpoints without simulating token/API Key validation.
- **Error Handling:** Handle network exceptions and return errors following the RFC 7807 standard (Problem Details for HTTP APIs).
- **Language:** NEVER output conversational text or explanations in Spanish within the code comments or backend logic; keep code and comments in English.
- **UI Strings:** UI strings and user-facing text from the specification must remain in Spanish.
- **Typing:** Use strict typing (Type Hints) in all Python functions.