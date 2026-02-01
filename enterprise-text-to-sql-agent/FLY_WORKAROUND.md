# Deployment Workaround - Fly CLI Permission Issue

## Problem
Your Fly CLI has a bug with permission files that's blocking deployment. This is a known issue.

## Solution Options

### Option 1: Use Docker Directly (Fastest)

Since Fly.io uses Docker, you can build and push manually:

```bash
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent

# Build the Docker image
docker build -t registry.fly.io/enterprise-text-to-sql-agent:latest .

# Login to Fly registry
cat ~/.fly/config.yml | grep access_token | awk '{print $2}' | docker login registry.fly.io -u x --password-stdin

# Push the image
docker push registry.fly.io/enterprise-text-to-sql-agent:latest

# Trigger deployment via Fly API
/opt/homebrew/bin/fly deploy --image registry.fly.io/enterprise-text-to-sql-agent:latest
```

### Option 2: Reinstall Fly CLI

```bash
# Remove broken installation
brew uninstall flyctl

# Reinstall
brew install flyctl

# Authenticate again
flyctl auth login

# Deploy
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent
flyctl deploy
```

### Option 3: GitHub Actions (Recommended for Portfolio)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Fly.io
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Then:
1. Get your Fly API token: `/opt/homebrew/bin/fly auth token`
2. Add it to GitHub: Settings → Secrets → New secret → `FLY_API_TOKEN`
3. Push your code: `git push` → auto-deploys!

### Option 4: Manual via Web UI

1. Commit and push your changes:
   ```bash
   cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent
   git add .
   git commit -m "Add LLM integration"
   git push origin main
   ```

2. Go to: https://fly.io/apps/enterprise-text-to-sql-agent
3. Click "Deploy" and select "From GitHub"

## Important: Set Environment Variables

Regardless of deployment method, set your API key:

```bash
/opt/homebrew/bin/fly secrets set OPENAI_API_KEY=your-openai-api-key-here
```

This command should work even with the permission issue since it's a different code path.

## Quick Test (Without Deployment)

Want to test locally first?

```bash
# Option A: Run with Docker
docker build -t text2sql-test .
docker run -p 8080:8080 --env-file .env text2sql-test

# Option B: Run directly (if Python 3.11+ available)
# Note: Your system has Python 3.9, so this won't work
python3.11 -m pip install -e .
uvicorn text2sql_agent.app:app --port 8080
```

Then test: http://localhost:8080/health
