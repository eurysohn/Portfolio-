# Security & Rate Limiting Enhancements

## ✅ Already Implemented (Backend)

### 1. Time-Based Rate Limiting
**File**: `src/text2sql_agent/app.py`

**Changes Made:**
- Upgraded from simple counter to time-windowed rate limiting
- **3 requests per 24 hours** per unique user (IP + cookie combination)
- Rate limit automatically resets after 24-hour window
- Provides clear time remaining in error messages

**Configuration via Environment Variables:**
```bash
RATE_LIMIT_MAX=3                    # Default: 3 requests
RATE_LIMIT_WINDOW_HOURS=24          # Default: 24 hours
DEMO_MODE=true                       # Enable/disable rate limiting
API_TOKEN=your_secret_token_here     # Optional: bypass token for you
```

### 2. Optional API Token Authentication
- Set `API_TOKEN` environment variable for authorized access
- You can bypass rate limits with: `Authorization: Bearer your_token`
- Useful for your own testing or giving access to trusted users

### 3. Better Error Messages
**Before:**
```json
{
  "detail": "I'm sorry, but to protect usage I've limited to 3 times per person.",
  "limit": 3
}
```

**After:**
```json
{
  "detail": "Demo limit reached: 3 requests per 24 hours. Please try again in 18 hour(s) and 42 minute(s).",
  "limit": 3,
  "window_hours": 24,
  "time_remaining": "18 hour(s) and 42 minute(s)",
  "message": "This is a public demo. For extended access, please contact the owner or deploy your own instance from the GitHub repository."
}
```

### 4. Demo Mode Information Endpoint
**New endpoint**: `GET /`

Returns:
```json
{
  "message": "Enterprise Text-to-SQL Agent",
  "demo_mode": true,
  "rate_limit": {
    "max_requests": 3,
    "window_hours": 24,
    "message": "Demo is limited to 3 requests per 24 hours per person"
  },
  "endpoints": {...}
}
```

## 📝 TODO: UI Enhancements (Needs Implementation)

### 1. Demo Banner Component
**Create**: `ui/src/components/DemoBanner.tsx`

```tsx
'use client'

import React from 'react'
import { AlertCircle, Github } from 'lucide-react'

const DemoBanner = () => {
  return (
    <div className="border-b border-amber-500/20 bg-amber-500/10 px-4 py-2">
      <div className="mx-auto flex max-w-4xl items-center justify-between gap-4 text-sm">
        <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400">
          <AlertCircle size={16} />
          <span className="font-medium">
            Public Demo: Limited to 3 requests per 24 hours
          </span>
        </div>
        <a
          href="https://github.com/eurysohn/Portfolio-/tree/main/enterprise-text-to-sql-agent"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-xs text-amber-700 hover:text-amber-800 transition-colors"
        >
          <Github size={14} />
          <span className="hidden sm:inline">Deploy your own</span>
        </a>
      </div>
    </div>
  )
}

export default DemoBanner
```

### 2. Update Page Layout
**Edit**: `ui/src/app/page.tsx`

```tsx
'use client'
import Sidebar from '@/components/chat/Sidebar/Sidebar'
import { ChatArea } from '@/components/chat/ChatArea'
import DemoBanner from '@/components/DemoBanner'
import { Suspense } from 'react'

export default function Home() {
  const hasEnvToken = false
  const envToken = ''
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="flex h-screen flex-col bg-background/80">
        <DemoBanner />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar hasEnvToken={hasEnvToken} envToken={envToken} />
          <ChatArea />
        </div>
      </div>
    </Suspense>
  )
}
```

### 3. Enhanced Rate Limit Error Handling
**Edit**: `ui/src/hooks/useAIStreamHandler.tsx`

Add better error display for rate limit errors (429 status).

## Important Note

**This is NOT an LLM-based system!** This project uses:
- ❌ No OpenAI API
- ❌ No Azure AI
- ❌ No external LLM calls
- ✅ Rule-based SQL generation (deterministic templates)
- ✅ Direct SQLite queries only

**Therefore:**
- No API keys are being consumed
- No external costs incurred
- Rate limiting is purely to prevent:
  - Server resource abuse
  - Database overload
  - Spam/DoS attempts

## Deployment with Environment Variables

### fly.toml Configuration
Add to your `fly.toml`:

```toml
[env]
  DEMO_MODE = "true"
  RATE_LIMIT_MAX = "3"
  RATE_LIMIT_WINDOW_HOURS = "24"

# Optional: Set via fly secrets for security
# Run: flyctl secrets set API_TOKEN=your_secret_token_here
```

### Local Development
Create `.env` file:

```bash
DEMO_MODE=false
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_HOURS=1
API_TOKEN=dev_token_12345
```

## Testing Rate Limits

### Test Normal User (Rate Limited)
```bash
# First 3 requests work
curl -X POST https://your-api.fly.dev/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "order fill rate last 30 days"}'

# 4th request returns 429
```

### Test with API Token (Bypasses Limits)
```bash
curl -X POST https://your-api.fly.dev/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_secret_token_here" \
  -d '{"question": "order fill rate last 30 days"}'
```

## Summary

### ✅ What's Protected Now
1. **Time-windowed rate limiting**: 3 requests per 24 hours (configurable)
2. **IP + Cookie tracking**: Prevents simple browser refresh abuse
3. **Clear user feedback**: Shows time remaining before retry
4. **Optional bypass**: API token for authorized users
5. **Demo mode flag**: Easy to disable for production

### 📋 Next Steps
1. Add UI banner showing demo limitations
2. Update page layout to include banner
3. Deploy with environment variables set
4. Test rate limiting in production

### 🔐 Recommended Settings for Public Demo

**Strict (Current):**
```bash
DEMO_MODE=true
RATE_LIMIT_MAX=3
RATE_LIMIT_WINDOW_HOURS=24
API_TOKEN=<your_secret_bypass_token>
```

**Moderate:**
```bash
DEMO_MODE=true
RATE_LIMIT_MAX=10
RATE_LIMIT_WINDOW_HOURS=24
```

**Development:**
```bash
DEMO_MODE=false
```

This ensures your demo stays available while preventing abuse!
