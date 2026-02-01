# Quick Deployment Guide

## The Issue
Fly.io CLI is experiencing permission errors preventing automated deployment. This is a local CLI configuration issue.

## Solution 1: Deploy via Terminal (Recommended)

Open your terminal and run these commands:

```bash
# Navigate to project
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent

# Deploy backend
fly deploy

# If that fails with permissions, try:
sudo fly deploy
```

You'll see build logs, and the deployment should complete in 2-3 minutes.

## Solution 2: Fix Fly CLI Permissions

If you keep seeing permission errors, fix the Fly CLI config:

```bash
# Remove and recreate the config directory
rm -rf ~/.fly
mkdir -p ~/.fly
chmod 700 ~/.fly

# Re-authenticate
fly auth login

# Then deploy
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent
fly deploy
```

## Solution 3: Web Dashboard Deployment

1. Go to https://fly.io/dashboard
2. Find your app: `enterprise-text-to-sql-agent`
3. Click "Deploy" → "Deploy from GitHub"
4. Connect your repo and trigger deployment

## What Will Be Deployed

The updated backend with:
- ✅ Real OpenAI LLM integration  
- ✅ Hybrid mode (rules + LLM fallback)
- ✅ Your API key configured via `.env`
- ✅ `/health` endpoint showing LLM status

## After Deployment

Test the LLM integration:

```bash
# Check health endpoint
curl https://enterprise-text-to-sql-agent.fly.dev/health

# You should see:
# {
#   "status": "ok",
#   "generator_mode": "hybrid",
#   "llm_enabled": true,
#   "llm_model": "gpt-4o-mini"
# }
```

## Setting Environment Variables on Fly.io

Your `.env` file is local only. To set the API key on Fly.io:

```bash
fly secrets set OPENAI_API_KEY=your-openai-api-key-here
```

This ensures the LLM works in production.

## Verify Deployment

Once deployed:

1. **Check health:** https://enterprise-text-to-sql-agent.fly.dev/health
2. **Test rule match:** 
   ```bash
   curl -X POST https://enterprise-text-to-sql-agent.fly.dev/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "order fill rate last 30 days"}'
   ```
3. **Test LLM fallback:**
   ```bash
   curl -X POST https://enterprise-text-to-sql-agent.fly.dev/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "show me the fill rate for orders in the past month"}'
   ```

The second one should trigger LLM mode and return intelligent SQL!
