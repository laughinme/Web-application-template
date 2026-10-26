# Frontend

Next.js App Router, React, strict TypeScript and Tailwind CSS 4. Requires Node.js 22 or newer.

```bash
npm ci
cp .env.example .env.local
npm run dev                 # http://localhost:3000
npm run dev:https           # optional local HTTPS
npm run check               # ESLint, TypeScript and production build
npm start                   # serve the production build
```

`src/app` owns routes, layouts and providers; `src/views` contains screen components.
`src/features`, `src/entities` and `src/shared` hold reusable application code.
Protected routes (`/`, `/profile`, `/dashboard`) restore the cookie session before rendering.
`/auth?next=/profile` returns to the requested local page after signing in.

API routing and environment presets: [README-dev.md](README-dev.md).
