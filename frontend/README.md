# Next.js

This template provides a minimal setup to get React working in Next.js with HMR and some ESLint rules.

Next.js includes the core tooling out of the box:

- Fast Refresh during development (HMR behavior)
- Built-in compiler/tooling (SWC and Turbopack), no Vite plugins required
- Native App Router and TypeScript support

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. For Next.js, use [`eslint-config-next`](https://nextjs.org/docs/app/api-reference/config/eslint) and consider adding TypeScript-aware rules via [`eslint-config-next/typescript`](https://nextjs.org/docs/app/api-reference/config/eslint#with-typescript).
