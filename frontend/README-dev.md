# Frontend development

## Local backend

Start the Docker stack from the repository root with `make up`. It includes nginx, which serves
presigned avatar uploads and public avatar URLs at `http://localhost/media-public/...`.

In `frontend/`:

```bash
npm ci
cp env-presets/local-backend.env .env.local
npm run dev
```

Open http://localhost:3000. Use `npm run dev:https` for local HTTPS with a generated certificate.
For an HTTP backend, leave `COOKIE_SECURE=false`; enable secure cookies when serving over HTTPS.

## API routing

The browser uses `/api/v1` by default. Next.js rewrites `/api/*` to `API_PROXY_TARGET`, so auth
cookies and CSRF work on the frontend origin without browser CORS requests. Docker nginx proxies
`/api/*` directly to FastAPI; other requests go to the Next.js server.

| Variable | Purpose |
| --- | --- |
| `API_PROXY_TARGET` | Server-side rewrite target; defaults to `http://localhost:8080` |
| `NEXT_PUBLIC_API_BASE_URL` | Optional browser-visible API origin for direct calls; empty uses the proxy |

Restart the dev server after changing `.env.local`. Production rewrites and `NEXT_PUBLIC_*`
values are fixed during `npm run build`; set these variables in the build environment.
`.env.local` is ignored by git and overrides `.env`.

## Remote backend

The proxy preset keeps requests on the frontend origin:

```bash
cp env-presets/live-backend-proxy.env .env.local
```

Set `API_PROXY_TARGET=https://your-api-domain`, then run `npm run dev` (or `dev:https` when the
backend issues secure cookies). Set the target on the deployment platform before building too.

Direct browser calls are available with `env-presets/live-backend-direct.env`. Set
`NEXT_PUBLIC_API_BASE_URL` to the backend origin. This bypasses the proxy and requires backend CORS
with credentials, compatible SameSite settings and a shared cookie domain so the frontend can
read the CSRF cookie. Use the proxy preset when frontend and backend have unrelated domains.
