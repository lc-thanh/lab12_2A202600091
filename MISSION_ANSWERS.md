# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcoded secrets trong code (OPENAI_API_KEY, DATABASE_URL) nên dễ lộ khi đẩy lên GitHub.
2. Không dùng environment variables cho cấu hình, nhiều giá trị bị hardcode.
3. Bật sẵn debug/reload, không an toàn cho môi trường production.
4. Dùng print để log và từng log cả API key, vi phạm bảo mật.
5. Không có endpoint health/readiness nên khó theo dõi và tự động restart trên cloud.
6. Host hardcode localhost nên không nhận kết nối từ bên ngoài container.
7. Port hardcode 8000 nên không tương thích cơ chế inject PORT của Railway/Render.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode trong code | Đọc từ env vars qua settings | Linh hoạt khi deploy, tránh lộ secrets |
| Health check | Không có | Có /health | Platform biết service còn sống để restart |
| Logging | print() thường | Structured JSON logging | Dễ parse và giám sát trên hệ thống log tập trung |
| Shutdown | Dừng đột ngột | Graceful shutdown (lifespan + SIGTERM) | Giảm rớt request đang xử lý |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: python:3.11
2. Working directory: /app
3. COPY requirements.txt trước để tận dụng layer cache, giúp build nhanh hơn khi source code đổi nhưng dependencies không đổi.
4. CMD là lệnh mặc định có thể bị ghi đè khi chạy container; ENTRYPOINT là lệnh chính cố định, đối số khi run sẽ nối thêm vào.

### Exercise 2.3: Image size comparison
- Develop: 1.66 GB
- Production: 236.44MB
- Difference: 85.76% (Production nhỏ hơn Develop, chênh khoảng 1,423.56 MB)

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: [lab12-production-b0a4.up.railway.app](https://lab12-production-b0a4.up.railway.app/)
- Screenshot: [railway_app.png](screenshots/railway_app.png), [railway_build_done.png](screenshots/railway_build_done.png), [railway_build_log.png](screenshots/railway_build_log.png), [railway_docs.png](screenshots/railway_docs.png)

## Part 4: API Security

### Exercise 4.1-4.3: Test results
Không có token:
```json
{"detail":"Authentication required. Include: Authorization: Bearer <token>"}
HTTP_STATUS=401
```

Token sai:
```json
{"detail":"Invalid token."}
HTTP_STATUS=403
```

Token đúng, gọi 12 lần liên tiếp:
- Lần 1-10: 200 OK, requests_remaining giảm từ 9 về 0
- Lần 11-12:
```json
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
```

Trả lời câu hỏi trong các mục 4.1-4.3:
1. API key/JWT được check ở đâu?
	- API key (bản develop) được check trong dependency `verify_api_key` qua header `X-API-Key`.
	- JWT (bản production) được check trong dependency `verify_token` qua header `Authorization: Bearer <token>`.
2. Điều gì xảy ra nếu sai key/sai token?
	- Thiếu thông tin xác thực: trả 401.
	- Thông tin xác thực không hợp lệ: trả 403.
3. Làm sao rotate key?
	- Đổi biến môi trường `AGENT_API_KEY` trên cloud/server rồi restart hoặc redeploy service.
	- Production nên cho phép giai đoạn chuyển tiếp chấp nhận đồng thời key cũ và key mới trong thời gian ngắn.
4. JWT flow:
	- Client gửi username/password vào endpoint lấy token.
	- Server trả JWT chứa `sub`, `role`, `iat`, `exp`.
	- Client gọi `/ask` kèm `Authorization: Bearer <token>`.
	- Server verify chữ ký + hạn token trước khi xử lý request.
5. Rate limiting dùng gì, limit bao nhiêu, bypass admin ra sao?
	- Algorithm: Sliding window (deque timestamp theo user).
	- User thường: 10 requests/phút.
	- Admin: dùng limiter riêng với ngưỡng cao hơn (100 requests/phút).

### Exercise 4.4: Cost guard implementation
Cách tôi triển khai theo code mẫu production:
1. Theo dõi usage theo user theo ngày (request count, input tokens, output tokens).
2. Quy đổi token sang chi phí USD theo đơn giá input/output.
3. Trước khi gọi LLM, kiểm tra budget user và budget toàn cục.
4. Nếu user vượt budget thì trả 402; nếu toàn cục vượt budget thì trả 503.
5. Sau khi có response thì record usage và cập nhật tổng chi phí.
6. Cảnh báo sớm khi mức dùng vượt ngưỡng (ví dụ 80%) để chủ động kiểm soát chi phí.

## Part 5: Scaling & Reliability

### Exercise 5.1: Health checks (develop)
Đã triển khai và chạy test trên `05-scaling-reliability/develop`.

Lệnh test:
```bash
curl -s http://localhost:8000/health
curl -s -w '\nHTTP_STATUS=%{http_code}\n' http://localhost:8000/ready
```

Kết quả thực tế:
```json
{"status":"ok","uptime_seconds":1.7,"version":"1.0.0","environment":"development","timestamp":"2026-04-17T13:53:34.448770+00:00","checks":{"memory":{"status":"ok","used_percent":36.3}}}
```

```json
{"ready":true,"in_flight_requests":1}
HTTP_STATUS=200
```

Kết luận: `/health` và `/ready` hoạt động đúng, trả 200 khi instance sẵn sàng.

### Exercise 5.2: Graceful shutdown (develop)
Đã test signal handling bằng cách gửi request rồi gửi `SIGTERM` ngay sau đó.

Kết quả thực tế:
```json
{"answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận."}
```

```text
POST_SHUTDOWN_READY_STATUS:
HTTP_STATUS=000
```

Log xác nhận graceful shutdown:
```text
INFO:     Shutting down
INFO:     Waiting for application shutdown.
... INFO 🔄 Graceful shutdown initiated...
... INFO ✅ Shutdown complete
INFO:     Application shutdown complete.
```

Kết luận: request đang xử lý vẫn hoàn tất trước khi tiến trình dừng, sau đó service không còn nhận request.

### Exercise 5.3: Stateless design (production)
Đã refactor để state nằm trong Redis (không lưu trong memory theo từng instance):
1. Session/history lưu theo key Redis (`session:<session_id>`).
2. Mọi agent instance đọc/ghi cùng nguồn state.
3. Có thêm endpoint `/ask` tương thích với hướng dẫn test và endpoint `/chat` cho multi-turn.

Kết quả kiểm chứng: cùng `session_id` vẫn giữ được history dù request đi qua các instance khác nhau.

### Exercise 5.4: Load balancing với Nginx (production)
Đã chạy stack:
```bash
docker compose up -d --build --scale agent=3
```

Kết quả thực tế từ header `X-Served-By` (18 requests):
```text
5  -> 172.18.0.3:8000
7  -> 172.18.0.4:8000
6  -> 172.18.0.5:8000
```

Kết luận: traffic được phân tán qua 3 instances, load balancing hoạt động đúng.

### Exercise 5.5: Test stateless
Đã chạy script:
```bash
python test_stateless.py
```

Kết quả thực tế:
1. 5 request được phục vụ bởi nhiều instance khác nhau (`instance-25385f`, `instance-656a19`, `instance-a0662d`).
2. Conversation history còn đủ `10` messages (5 user + 5 assistant).
3. Script báo: `Session history preserved across all instances via Redis!`

Test failover bổ sung (kill 1 instance):
1. Tạo session mới, nhận `session_id`.
2. `docker stop production-agent-3`.
3. Gửi tiếp request cùng `session_id` và kiểm tra history.

Kết quả thực tế:
```text
FIRST_SERVED_BY= instance-656a19
STOPPING= production-agent-3
SECOND_SERVED_BY= instance-a0662d
HISTORY_COUNT= 4
LAST_USER= after kill
```

Kết luận: khi một instance chết, request tiếp theo vẫn xử lý được và session không mất nhờ Redis.
