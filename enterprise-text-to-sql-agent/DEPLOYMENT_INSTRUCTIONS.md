# How to Deploy UI Changes

## Issue
The recommended questions component exists in the code but isn't showing up on the live demo.

## Root Cause
The changes are in your local codebase but haven't been deployed to Fly.io yet.

## Solution: Deploy the UI

### Step 1: Verify Changes Are Saved
```bash
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent

# Check what files have changed
git status

# You should see:
# - ui/src/components/chat/ChatArea/Messages/Messages.tsx (modified)
# - ui/src/components/chat/ChatArea/Messages/RecommendedQuestions.tsx (new file)
# - ui/src/components/chat/ChatArea/Messages/ChatBlankState.tsx (modified)
# - ui/src/components/ui/typography/MarkdownRenderer/styles.tsx (modified)
# - src/text2sql_agent/app.py (modified - for backend markdown)
```

### Step 2: Commit All Changes
```bash
git add .
git commit -m "Add persistent recommended questions, prettier UI with markdown formatting, and enhanced rate limiting"
git push origin main
```

### Step 3: Deploy Backend (for markdown improvements)
```bash
# From root directory
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent
flyctl deploy
```

Wait for deployment to complete (~2-3 minutes).

### Step 4: Deploy UI (for recommended questions)
```bash
# Go to UI directory
cd ui
flyctl deploy
```

Wait for deployment to complete (~2-3 minutes).

### Step 5: Verify
1. Open https://enterprise-text-to-sql-agent-ui.fly.dev
2. Ask a question (e.g., "Order fill rate last 30 days")
3. After the response appears, scroll down
4. You should now see: "💡 Try another question:" with buttons below

## Quick Deploy Script

Or run this all at once:

```bash
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent

# Commit changes
git add .
git commit -m "Add persistent recommended questions and prettier markdown UI"
git push origin main

# Deploy backend
flyctl deploy

# Deploy UI
cd ui
flyctl deploy

echo "✅ Deployment complete! Check https://enterprise-text-to-sql-agent-ui.fly.dev"
```

## What You Should See After Deployment

### Before (Current):
- Welcome screen shows questions
- After asking one question, questions disappear
- Only see messages

### After (New):
- Welcome screen shows questions (prettier version)
- After asking a question, see the formatted response
- **At the bottom**: "💡 Try another question:" with 8 question buttons
- Questions persist throughout the entire chat session

## Troubleshooting

### If recommended questions still don't show:
1. Hard refresh the page (Cmd+Shift+R or Ctrl+Shift+R)
2. Clear browser cache
3. Check browser console for errors (F12 → Console tab)
4. Verify deployment succeeded: `flyctl status --app enterprise-text-to-sql-agent-ui`

### If you see build errors:
1. Make sure you're in the correct directory
2. Check that all imports are correct
3. Run `flyctl logs --app enterprise-text-to-sql-agent-ui` to see deployment logs
