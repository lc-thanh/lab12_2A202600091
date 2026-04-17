# Lab 12 — Complete Production Agent

Kết hợp TẤT CẢ những gì đã học trong 1 project hoàn chỉnh.

## Checklist Deliverable

- [x] Dockerfile (multi-stage, < 500 MB)
- [x] docker-compose.yml (agent + redis)
- [x] .dockerignore
- [x] Health check endpoint (`GET /health`)
- [x] Readiness endpoint (`GET /ready`)
- [x] API Key authentication
- [x] Rate limiting
- [x] Cost guard
- [x] Config từ environment variables
- [x] Structured logging
- [x] Graceful shutdown
- [x] Public URL ready (Railway / Render config)

---

## Cấu Trúc

```
06-lab-complete/
├── app/
│   ├── main.py         # Entry point — kết hợp tất cả
│   ├── config.py       # 12-factor config
│   ├── auth.py         # API Key auth
│   ├── conversation.py # Conversation history in Redis
│   ├── rate_limiter.py # Rate limiting
│   └── cost_guard.py   # Budget protection
├── utils/
│   └── mock_llm.py     # Mock LLM dùng cho lab
├── Dockerfile          # Multi-stage, production-ready
├── docker-compose.yml  # Full stack
├── nginx/              # Nginx load balancer
├── railway.toml        # Deploy Railway
├── render.yaml         # Deploy Render
├── .env.example        # Template
├── .dockerignore
└── requirements.txt
```

---

## Chạy Local

```bash
# 1. Setup
cp .env.example .env

# 2. Chạy với Docker Compose
docker compose up --scale agent=3

# 3. Test
curl http://localhost:8080/health

# 4. Lấy API key từ .env, test endpoint
API_KEY=$(grep AGENT_API_KEY .env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" \
     -X POST http://localhost:8080/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is deployment?"}'
```

Conversation history được lưu trong Redis. Gửi thêm `conversation_id` trong body nếu muốn tiếp tục một cuộc hội thoại; xem lại lịch sử bằng `GET /conversations/{conversation_id}`.

### LLM mode (OpenAI + fallback)

- Nếu `OPENAI_API_KEY` hợp lệ: app ưu tiên gọi OpenAI thật.
- Nếu thiếu key hoặc gọi OpenAI lỗi tạm thời: app fallback về mock để không gián đoạn dịch vụ.
- Nguồn trả lời (`openai`, `mock`, `mock_fallback`) được ghi trong structured logs (`agent_call.llm_source`).

---

## Deploy Railway (< 5 phút)

```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login và deploy
railway login
railway init
railway variables set OPENAI_API_KEY=sk-...
railway variables set AGENT_API_KEY=your-secret-key
railway variables set REDIS_URL=redis://<your-redis-host>:6379/0
railway up

# Nhận public URL!
railway domain
```

---

## Deploy Render

1. Push repo lên GitHub
2. Render Dashboard → New → Blueprint
3. Connect repo → Render đọc `render.yaml`
4. Set secrets: `OPENAI_API_KEY`, `AGENT_API_KEY`, `REDIS_URL`
5. Deploy → Nhận URL!

---

## Kiểm Tra Production Readiness

```bash
python check_production_ready.py
```

Script này kiểm tra tất cả items trong checklist và báo cáo những gì còn thiếu.
