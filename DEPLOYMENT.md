# Deployment Information

## Public URL
https://lab12-06-production.up.railway.app

## Platform
Railway (CLI)

## Service
- Project: lab12
- Service: lab12-06
- Redis service: Redis

## Test Commands

### Health Check
```bash
curl https://lab12-06-production.up.railway.app/health
# Expected: {"status":"ok", ...}
```

Actual output (2026-04-18):
```json
{"status":"ok","version":"1.0.0","environment":"production","uptime_seconds":213.5,"total_requests":4,"redis_connected":true,"monthly_budget_usd":10.0,"timestamp":"2026-04-17T17:07:52.196316+00:00"}
HTTP_STATUS=200
```

### API Test (authentication required)
```bash
curl -X POST https://lab12-06-production.up.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

Actual output (2026-04-18):
```json
{"question":"Hi, answer in one short sentence.","answer":"Sure! What would you like to know?","conversation_id":"user-0e68c147e45fd617","history_messages":22,"model":"gpt-4o-mini","timestamp":"2026-04-17T17:07:54.943381+00:00"}
HTTP_STATUS=200
```

### Auth Check (no API key)
```bash
curl -X POST https://lab12-06-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
# Expected: HTTP 401
```

Actual output (2026-04-18):
```json
{"detail":"Missing X-API-Key header"}
HTTP_STATUS=401
```

### Rate Limit Check
```bash
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://lab12-06-production.up.railway.app/ask \
    -H "X-API-Key: YOUR_KEY" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"test","question":"rate limit test"}'
done
# Expected: after threshold, HTTP 429
```

Actual output (2026-04-18):
```text
200 200 200 200 200 200 200 200 200 429 429 429 429 429 200
```

Note: the sequence shows `429` after threshold, proving rate limiting is active.

## Verified Results (2026-04-18)

- Health check: HTTP 200
- Readiness check: HTTP 200
- Ask without key: HTTP 401
- Ask with valid key: HTTP 200
- Rate limit (15 calls): `200 200 200 200 200 200 200 200 200 429 429 429 429 429 200`

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- JWT_SECRET
- LOG_LEVEL
- OPENAI_API_KEY
- ENVIRONMENT

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
