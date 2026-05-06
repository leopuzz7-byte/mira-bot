# 🌿 Мира — Telegram-бот

## Быстрый старт

### 1. Получи токен бота
1. Открой Telegram, найди @BotFather
2. `/newbot` → задай имя и username (например `MiraHelperBot`)
3. Скопируй токен вида `123456789:ABC...`

### 2. Получи API-ключ для ИИ
**Claude (Anthropic):** https://console.anthropic.com → API Keys  
**OpenAI/GPT-4:** https://platform.openai.com → API Keys

### 3. Настрой .env
```bash
cp .env.example .env
```
Открой `.env` и вставь свои ключи.

### 4. Запуск через Docker (рекомендуется)
```bash
docker-compose up -d
```

### 4b. Запуск напрямую (без Docker)
```bash
pip install -r requirements.txt
python main.py
```

---

## Смена AI-провайдера
Просто поменяй строки в `.env`:

```env
# GPT-4o
AI_PROVIDER=openai
AI_MODEL=gpt-4o
OPENAI_API_KEY=sk-...

# Claude Sonnet
AI_PROVIDER=claude
AI_MODEL=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Команды бота
| Команда | Действие |
|---------|----------|
| `/start` | Начать / вернуться в меню |
| `/diary` | Дневник состояния |
| `/sos` | Помощь при срыве |
| `/chat` | Поговорить с Мирой |
| `/help` | Справка |

---

## Деплой на сервер (VPS)
```bash
git clone <твой репо>
cd mira_bot
cp .env.example .env   # заполни ключи
docker-compose up -d
docker-compose logs -f  # смотреть логи
```
# Mira Bot — последнее обновление: 2026-05-06 23:07
