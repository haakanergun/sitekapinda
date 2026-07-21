# Codex Model Routing

The plugin manifest intentionally does not select a model. Model access belongs to the user's Codex configuration or scheduled-task setup.

The Build Week workflow used GPT-5.6-family Codex models for research, architecture, implementation, review, and creative direction. A quality-first installation can use GPT-5.6 Sol with high reasoning for creative direction, implementation, policy escalation, and final QA. Lower-cost discovery or extraction may use another GPT-5.6 profile available to the user's account.

Never silently substitute a model when a requested profile is unavailable. Report the incompatibility and let the user choose. Persist the selected model, reasoning level, prompt version, and artifact version in any production implementation.

