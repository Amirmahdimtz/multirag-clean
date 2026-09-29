# راهنمای استقرار Production پروژه MultiRAG

## 1. معماری نهایی

Compose سه سرویس را روی شبکه داخلی `backend` اجرا می‌کند:

1. `app`: برنامه FastAPI، با پورت داخلی 8000 و پورت عمومی پیش‌فرض 2011.
2. `postgres`: PostgreSQL 16 به‌همراه افزونه pgvector؛ بدون پورت عمومی.
3. `vllm`: API سازگار با OpenAI روی پورت داخلی 8000؛ بدون پورت عمومی و تنها سرویس دارای GPU.

داده‌های PostgreSQL، فایل‌های آپلودشده، cache مدل vLLM و cache مدل embedding در چهار volume مستقل نگهداری می‌شوند. حذف و ایجاد مجدد containerها این داده‌ها را حذف نمی‌کند.

برنامه از آدرس داخلی زیر برای LLM استفاده می‌کند:

```text
http://vllm:8000/v1
```

مدل embedding فعلی `jinaai/jina-embeddings-v3` داخل container برنامه و روی CPU اجرا می‌شود. یک سرویس vLLM نمی‌تواند هم‌زمان یک مدل chat و یک مدل embedding جداگانه را سرو کند؛ بنابراین برای حفظ معماری و قرارداد فعلی `IEmbeddingService`، embedding به vLLM منتقل نشده است.

## 2. پروفایل انتخاب‌شده برای server215

این نسخه برای سخت‌افزار واقعی زیر تنظیم شده است:

- یک NVIDIA A100-SXM4 با 40GB VRAM
- NVIDIA Driver 550.54.14
- حدود 78GiB RAM
- مدل موردنظر Gemma 4 31B

مدل BF16 رسمی `google/gemma-4-31B-it` حدود 69.9GB حافظه برای load نیاز دارد و روی این GPU جا نمی‌شود. بنابراین checkpoint رسمی QAT چهار‌بیتی زیر انتخاب شده است:

```text
google/gemma-4-31B-it-qat-w4a16-ct
```

تنظیم اولیه شامل یک GPU، context برابر 16384، مصرف حداکثر 90 درصد VRAM و غیرفعال‌کردن profiling تصویر و صدا است؛ MultiRAG فعلی فقط prompt متنی به LLM می‌فرستد. اگر load test با ترافیک واقعی موفق بود می‌توان context یا concurrency را مرحله‌ای افزایش داد.

پارامترهای generation نیز مطابق توصیه مدل تنظیم شده‌اند: `temperature=1.0`، `top_p=0.95` و `top_k=64`. مقدار `top_k` از طریق `extra_body` کلاینت OpenAI-compatible برای vLLM ارسال می‌شود.

## 3. پیش‌نیازهای سرور

- Linux 64-bit
- Docker Engine و Docker Compose plugin جدید
- درایور سازگار NVIDIA
- NVIDIA Container Toolkit
- فضای کافی برای image بزرگ vLLM و cache مدل‌ها

بررسی اولیه:

```bash
docker --version
docker compose version
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
```

نیازی نیست CUDA Toolkit داخل container برنامه FastAPI نصب یا GPU به آن متصل شود.

## 4. تنظیم environment

در ریشه پروژه:

```bash
cp .env.example .env
nano .env
chmod 600 .env
```

حداقل این مقادیر را تغییر دهید:

```dotenv
POSTGRES_PASSWORD=...
MULTIRAG_DATABASE_URL=postgresql+asyncpg://multirag:URL_ENCODED_PASSWORD@postgres:5432/multirag
MULTIRAG_ADMIN_API_KEYS=["..."]
MULTIRAG_USER_API_KEYS=[{"api_key":"...","user_id":"..."}]
VLLM_IMAGE=vllm/vllm-openai:gemma4
VLLM_MODEL=google/gemma-4-31B-it-qat-w4a16-ct
VLLM_SERVED_MODEL_NAME=gemma4-31b
VLLM_API_KEY=...
HF_TOKEN=...
VLLM_TENSOR_PARALLEL_SIZE=1
VLLM_MAX_MODEL_LEN=16384
VLLM_GPU_MEMORY_UTILIZATION=0.90
VLLM_ENABLE_CUDA_COMPATIBILITY=1
```

ابتدا شرایط استفاده Gemma را در Hugging Face بپذیرید و یک token فقط‌خواندنی در `HF_TOKEN` قرار دهید. تنظیم compatibility برای image رسمی Gemma 4 که بر پایه CUDA 12.9 است و driver فعلی 550 فعال شده است.

پس از pull و تست موفق، image شناور را به digest همان image قفل کنید:

```bash
docker pull vllm/vllm-openai:gemma4
docker image inspect vllm/vllm-openai:gemma4 \
  --format '{{index .RepoDigests 0}}'
```

خروجی را به‌صورت `repository@sha256:...` در `VLLM_IMAGE` قرار دهید.

اگر password دیتابیس کاراکترهایی مانند `@`، `:`، `/` یا `#` دارد، نسخه URL-encoded آن را فقط در `MULTIRAG_DATABASE_URL` قرار دهید. مقدار خام همان password در `POSTGRES_PASSWORD` می‌ماند.

سه مقدار زیر باید یکسان باشند؛ مقدار پیش‌فرض همه 1024 است:

```dotenv
MULTIRAG_EMBEDDING_VECTOR_SIZE=1024
MULTIRAG_PGVECTOR_VECTOR_SIZE=1024
# بُعد خروجی واقعی مدل embedding نیز باید 1024 باشد.
```

فایل `.env` نباید commit یا داخل image کپی شود؛ `.gitignore` و `.dockerignore` آن را حذف می‌کنند.

## 5. اعتبارسنجی، build و اجرا

```bash
docker compose --env-file .env config --quiet
docker compose --env-file .env build --pull app
docker compose --env-file .env pull postgres vllm
docker compose --env-file .env up -d postgres
docker compose --env-file .env run --rm --no-deps app alembic upgrade head
docker compose --env-file .env up -d
```

سرویس `app` فقط بعد از healthy شدن PostgreSQL و vLLM ساخته و اجرا می‌شود. اولین اجرای vLLM و Jina ممکن است به‌دلیل دانلود مدل‌ها طولانی باشد.

وضعیت و logها:

```bash
docker compose --env-file .env ps
docker compose --env-file .env logs -f --tail=200
docker compose --env-file .env logs -f --tail=200 app
docker compose --env-file .env logs -f --tail=200 postgres
docker compose --env-file .env logs -f --tail=200 vllm
```

## 6. تست سلامت بعد از deployment

تست کامل خودکار:

```bash
chmod +x deploy/healthcheck.sh
./deploy/healthcheck.sh
```

تست دستی API از host:

```bash
curl -fsS http://127.0.0.1:2011/api/v1/health/
```

تست PostgreSQL داخل شبکه Compose:

```bash
docker compose --env-file .env exec postgres \
  sh -ec 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

تست health خود vLLM:

```bash
docker compose --env-file .env exec vllm \
  python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5); print('ok')"
```

PostgreSQL و vLLM عمداً از host قابل دسترسی نیستند. تست آن‌ها باید با `docker compose exec` یا از سرویس `app` انجام شود.

## 7. عملیات روزمره

Build مجدد برنامه:

```bash
docker compose --env-file .env build app
```

شروع یا اعمال تغییرات Compose:

```bash
docker compose --env-file .env up -d --remove-orphans
```

توقف بدون حذف container و volume:

```bash
docker compose --env-file .env stop
```

توقف و حذف container/network، با حفظ volumeها:

```bash
docker compose --env-file .env down
```

Restart یک سرویس:

```bash
docker compose --env-file .env restart app
docker compose --env-file .env restart vllm
docker compose --env-file .env restart postgres
```

هرگز در Production بدون backup از `docker compose down -v` استفاده نکنید؛ این دستور volumeهای دائمی را حذف می‌کند.

## 8. روند امن update

1. از دیتابیس و فایل‌های آپلودشده backup بگیرید.
2. migrationهای نسخه جدید را روی restore همان backup آزمایش کنید.
3. نسخه imageهای `PGVECTOR_IMAGE` و `VLLM_IMAGE` را آگاهانه تغییر دهید.
4. Compose را validate کنید.
5. imageها را pull/build کنید.
6. migration را اجرا کنید.
7. سرویس‌ها را recreate و health check کنید.

```bash
docker compose --env-file .env config --quiet
docker compose --env-file .env pull postgres vllm
docker compose --env-file .env build --pull app
docker compose --env-file .env up -d postgres
docker compose --env-file .env run --rm --no-deps app alembic upgrade head
docker compose --env-file .env up -d --remove-orphans
./deploy/healthcheck.sh
```

برای rollback باید tag قبلی imageها و backup دیتابیس در دسترس باشد. قبل از upgrade نسخه اصلی PostgreSQL، راهنمای رسمی upgrade و سازگاری pgvector را بررسی کنید.

## 8.1. مدیریت migration دیتابیس

تغییرات schema با Alembic نسخه‌بندی می‌شوند. قبل از هر deployment:

```bash
docker compose --env-file .env up -d postgres
docker compose --env-file .env run --rm --no-deps app alembic upgrade head
```

برای دیتابیس قدیمی `v0.1.0` فقط وقتی schema دقیقاً با migration اولیه
تطبیق داده شده و backup معتبر دارید، می‌توان revision اولیه را stamp کرد:

```bash
docker compose --env-file .env run --rm --no-deps app \
  alembic stamp 0001_initial_schema
```

روی دیتابیس ناشناخته یا تغییر‌یافته از `stamp` استفاده نکنید.

## 9. Backup پایه PostgreSQL

```bash
mkdir -p backups
docker compose --env-file .env exec -T postgres \
  sh -ec 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  | gzip > "backups/multirag-$(date +%F-%H%M%S).sql.gz"
```

backup باید خارج از همان دیسک و ترجیحاً در storage جداگانه نگهداری و restore آن دوره‌ای آزمایش شود. volume آپلودها نیز باید با ابزار backup سازمان نسخه‌برداری شود.

## 10. اجرای دائمی و systemd اختیاری

وجود `restart: unless-stopped` و فعال بودن Docker در boot معمولاً کافی است:

```bash
sudo systemctl enable --now docker
```

اگر مدیریت stack با systemd الزام سازمان است:

```bash
sudo mkdir -p /opt/multirag
# پروژه و .env را در /opt/multirag قرار دهید.
sudo cp deploy/multirag-compose.service.example \
  /etc/systemd/system/multirag-compose.service
sudo systemctl daemon-reload
sudo systemctl enable --now multirag-compose.service
sudo systemctl status multirag-compose.service
```

اگر مسیر پروژه متفاوت است، `WorkingDirectory` فایل service را قبل از فعال‌سازی اصلاح کنید.

## 11. نکات امنیت و شبکه

- فقط پورت 2011 برنامه publish شده است.
- vLLM با API key محافظت می‌شود، ولی چون endpointهای غیر `/v1` ممکن است احراز هویت یکسان نداشته باشند، نباید مستقیماً روی اینترنت publish شود.
- دسترسی پورت 2011 را با firewall یا reverse proxy محدود و TLS را در reverse proxy فعال کنید.
- secretها را داخل Dockerfile، Compose، repository یا log قرار ندهید.
- `.env` را با permission محدود نگه دارید و کلیدها را دوره‌ای rotate کنید.
- endpointهای API خود MultiRAG را با کلیدهای تصادفی و منحصربه‌فرد محافظت کنید.

## 12. عیب‌یابی سریع

اگر `vllm` unhealthy است:

```bash
docker compose --env-file .env logs --tail=300 vllm
nvidia-smi
```

علت‌های متداول: کمبود VRAM، ناسازگاری مدل با vLLM، نیاز به `HF_TOKEN`، طول context بیش از ظرفیت، یا اشتباه بودن tensor parallel.

اگر `app` بالا نمی‌آید:

```bash
docker compose --env-file .env logs --tail=300 app
docker compose --env-file .env ps
```

در اولین اجرا، دانلود و load مدل embedding روی CPU زمان‌بر است. اگر حالت offline فعال باشد، `MULTIRAG_EMBEDDING_LOCAL_PATH` باید به مسیر موجود داخل volume مدل اشاره کند.