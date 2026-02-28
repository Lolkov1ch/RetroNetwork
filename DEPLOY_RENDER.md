# Deploying RetroNetwork to Render

This document lists the steps to deploy the project using Render (Docker).

1. Connect repository
- On Render, create a new **Web Service** and connect your GitHub/GitLab repo and select the branch to deploy.
- Choose **Docker** (use the repository Dockerfile).

2. Environment variables (set in Render service settings)
- `DATABASE_URL` — provided by Render Managed Postgres or paste your DB URL (e.g. `postgresql://user:pass@host:5432/dbname`).
- `SECRET_KEY` — a strong secret (keep private).
- `DEBUG` — set to `False`.
- `ALLOWED_HOSTS` — comma-separated hostnames (include your Render URL, e.g. `retronetwork.onrender.com`).
- `REDIS_HOST` / `REDIS_PORT` — if using Redis; use Render Redis add-on or managed Redis provider.
- Optional: `CORS_ALLOWED_ORIGINS`, `DJANGO_LOG_LEVEL`, other settings from `.env.example`.

3. Provision a managed Postgres on Render (recommended)
- Create a new Render Postgres instance and attach it to your Web service. Render will populate `DATABASE_URL` automatically.

4. Build & deploy
- Trigger a deploy on Render once env vars are set.
- Render will build the Docker image, run the container, and use the `docker-entrypoint.sh` script to run migrations and collect static files.

5. Post-deploy validation
- Check Render build and runtime logs for errors (migrations, collectstatic, permissions).
- Visit your service URL: `https://<your-service>.onrender.com`.
- Run health check: `curl -I https://<your-service>.onrender.com`.

Notes and tips
- The Dockerfile runs the app as non-root `appuser` for better security. The image sets ownership of `/app` and subfolders during build to `appuser`.
- If you need persistent storage for media, attach a Render persistent volume and ensure the correct permissions — Render's volume ownership may require additional setup; if collectstatic or uploads fail due to permissions, you can use an init command to `chown` the mounted directory at container start (requires running as root briefly) or set the volume mount options in Render.
- Keep secrets out of the repo and only set them in the Render Dashboard.

Troubleshooting
- `PermissionError` during `collectstatic`: ensure the target static/media directories are writable by the container user. On Render, prefer letting the image own the directories and avoid mounting host-owned volumes with incompatible permissions.
- DB connection errors: check `DATABASE_URL`, ensure the DB accepts connections from Render and that credentials are correct.

If you want, I can:
- Push these changes to the current branch and trigger a deploy (if you want me to run git push here).
- Add a small `render.yaml` manifest for infra-as-code for Render.

