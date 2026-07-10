# گزارش رفع ایراد شماره 12: Docker و Production Deployment

## وضعیت قبل از اصلاح

- پروژه `multirag-clean` فاقد Dockerfile، Compose و راهنمای Production بود.
- host برنامه `127.0.0.1` بود و از environment قابل تغییر نبود.
- LLM از `langchain-ollama` و `ChatOllama` استفاده می‌کرد.
- provider پیش‌فرض Production برای vector store مشخص نشده بود.
- مدل Jina داخل برنامه device را خودکار انتخاب می‌کرد و می‌توانست GPU برنامه را مصرف کند.
- فایل `.env.example` دارای credentialهای نمونه ضعیف و تنظیمات قدیمی Ollama بود.
- تنظیمات pool دیتابیس در config وجود داشت، اما به `DbContext` تزریق نمی‌شد.

## تغییرات اعمال‌شده

- Dockerfile چندمرحله‌ای با Python 3.10، کاربر non-root، PyTorch CPU-only و healthcheck ساخته شد.
- `compose.yaml` شامل `app`، `postgres`/pgvector و `vllm` اضافه شد.
- فقط پورت `2011` برنامه روی host publish شده است.
- PostgreSQL و vLLM فقط روی شبکه داخلی `backend` در دسترس‌اند.
- healthcheck مستقل برای هر سه سرویس و `depends_on: condition: service_healthy` اضافه شد.
- restart policy، stop grace period و volumeهای دائمی PostgreSQL، uploads، vLLM و embedding اضافه شد.
- آداپتر Ollama با `VLLMChatModelService` مبتنی بر OpenAI-compatible API جایگزین شد.
- wiring در `InfrastructureCollection` تغییر کرد؛ قرارداد `IChatModelService`، Core و Application دست‌نخورده ماندند.
- همه تنظیمات مدل، API key، آدرس vLLM، generation، دیتابیس، embedding و مسیر storage از environment خوانده می‌شوند.
- embedding فعلی Jina داخل app و روی CPU تثبیت شد؛ app هیچ GPU reservation ندارد.
- اتصال PostgreSQL اصلی و PGVector از همان `DbContext` و `MULTIRAG_DATABASE_URL` انجام می‌شود؛ کلید بلااستفاده دوم حذف شد.
- تنظیمات pool دیتابیس به `DbContext` تزریق و `pool_pre_ping` فعال شد.
- `.dockerignore`، `.env.example` امن، healthcheck script، راهنمای کامل و unit نمونه systemd اضافه شد.

## بررسی‌های انجام‌شده

- compile استاتیک تمام 166 فایل Python: موفق
- parse فایل `config/config.yaml`: موفق
- resolve مقادیر Production توسط `ConfigReader`: موفق
- parse و interpolation فایل Compose با مقادیر نمونه: موفق
- کنترل سه سرویس، dependencyهای healthy، شبکه، چهار volume و پورت `2011`: موفق
- کنترل عدم publish پورت PostgreSQL و vLLM: موفق
- کنترل اختصاص GPU فقط به vLLM: موفق
- کنترل shell syntax فایل `deploy/healthcheck.sh`: موفق
- جست‌وجوی کامل Ollama در سورس قابل‌تحویل: بدون نتیجه
- کنترل placeholder بودن secretهای `.env.example`: موفق

## پروفایل قطعی سرور مقصد

- GPU: یک `NVIDIA A100-SXM4 40GB`
- Driver: `550.54.14`
- RAM: حدود 78GiB
- Docker: `29.6.1`
- Docker Compose: `5.3.1`
- مدل درخواستی: Gemma 4 31B
- checkpoint انتخاب‌شده: `google/gemma-4-31B-it-qat-w4a16-ct`
- vLLM image: `vllm/vllm-openai:gemma4`
- tensor parallel: یک GPU
- context اولیه: 16384 token

نسخه BF16 مدل 31B حدود 69.9GB حافظه بارگذاری نیاز دارد و روی GPU چهل‌گیگ قابل اجرا نیست. checkpoint رسمی QAT چهار‌بیتی برای vLLM انتخاب شده است تا مدل روی یک A100 چهل‌گیگ اجرا شود و فضای لازم برای runtime و KV cache باقی بماند.

موارد باقی‌مانده فقط پذیرش عملیاتی روی خود سرور هستند: pull/build واقعی، دانلود checkpoint، load مدل، پاسخ chat completion و تست end-to-end پورت 2011.

## نتیجه

کمبودهای کدنویسی و فایل‌های مربوط به ایراد 12 برطرف شده‌اند و پروفایل مدل/GPU نیز تعیین شده است. بستن عملیاتی ایراد بعد از موفق شدن این دو دستور روی سرور انجام می‌شود:

```bash
docker compose --env-file .env up -d
./deploy/healthcheck.sh
```

اگر healthcheck کامل موفق شود، ایراد 12 هم از نظر پیاده‌سازی و هم از نظر acceptance محیط Production بسته است.

نکته خارج از دامنه مستقیم ایراد 12: پروژه هنوز برای تغییرات آینده schema از `Base.metadata.create_all` استفاده می‌کند و migration versioned مانند Alembic ندارد. این موضوع مانع اولین deployment نیست، اما قبل از تغییر schema در Production باید جداگانه حل شود.