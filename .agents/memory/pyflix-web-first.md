---
name: PyFlix web-first requirements
description: Durable product scope and workflow expectations for the PyFlix project.
---

PyFlix is a web-only project. Keep the catalog dynamic: film metadata and relative image/video paths come from the database, while the media files stay in suitable static or object storage. The intended practice path is a web prototype, Flask and database integration, tests, GitHub, then a hosted deployment with persistent PostgreSQL.

**Why:** the user described this as the goal in the project audio and wants the implementation to be practical, not a desktop-renderer exercise.

**How to apply:** prefer web technologies and database-backed catalog flows; keep local SQLite for development and require a persistent database for production. Never publish local account databases or secrets to GitHub.
