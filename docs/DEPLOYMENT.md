# Deployment Guide

## Quick Deploy (Recommended)

Deploy both AI service and frontend with one command:

```bash
make deploy-all
```

This will:

1. Start the AI service with ngrok
2. Automatically get the new ngrok URL
3. Update the frontend config
4. Deploy to Netlify

Logs are saved to `logs/deploy-all.log`.

---

## Manual Deployment

### 1. Deploy AI Service

```bash
cd services/ai
make prod
```

Copy the ngrok URL from the output (e.g., `https://abc123.ngrok-free.app`).

### 2. Update Frontend Config

Edit `services/frontend/netlify.toml`:

```toml
NEXT_PUBLIC_API_BASE_URL = "https://YOUR-NGROK-URL.ngrok-free.app"
```

### 3. Deploy Frontend

```bash
cd scripts
./deploy-frontend-service.sh
```

Or manually:

```bash
cd services/frontend
make clean && make build
netlify deploy --prod
```

---

## Other Commands

| Command                | Description                     |
| ---------------------- | ------------------------------- |
| `make deploy-all`      | Full deployment (AI + Frontend) |
| `make deploy-frontend` | Deploy frontend only            |
| `make clean`           | Clean build artifacts           |
| `make help`            | Show all available commands     |

---

## Troubleshooting

**Ngrok URL not found:**

- Check if ngrok is running: `http://localhost:4040`
- Verify the AI service started correctly

**Netlify deploy fails:**

- Ensure you're logged in: `netlify login`
- Check build errors in the terminal output
