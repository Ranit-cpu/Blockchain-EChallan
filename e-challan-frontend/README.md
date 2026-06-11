# e-Challan Frontend

Production-ready React + Vite frontend for a blockchain-based e-Challan system.

## Stack

- React 18+ / Vite
- Tailwind CSS + ShadCN-style UI (Radix)
- React Router DOM
- Axios (cookie sessions)
- Zustand
- TanStack React Query
- React Hook Form + Zod
- Framer Motion
- Recharts
- Socket.IO Client

## Quick Start

```bash
cp .env.example .env
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Docker

```bash
docker compose up --build
```

Frontend: http://localhost:3000

## Environment

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | FastAPI backend base URL |
| `VITE_WS_URL` | Socket.IO server URL |
| `VITE_APP_NAME` | Application display name |

## Roles

- **admin** — Full system access
- **officer** — Issue challans, upload evidence
- **owner** — View/pay challans, verify authenticity
