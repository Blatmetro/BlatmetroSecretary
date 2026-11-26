# 🤖 Blatmetro Secretary

**Личный Telegram-ассистент на базе локальной языковой модели Qwen2.5-0.5B-Instruct.**

Blatmetro Secretary — проект Telegram-бота, предназначенного для помощи в личной переписке, работе с текстами и повседневных задачах.

Проект разработан Blatmetro с использованием ИИ-инструментов **ChatGPT** и **OpenAI Codex**.

## ✨ Возможности

- 💬 Общение и ответы на вопросы.
- ✍️ Составление и редактирование сообщений.
- 🌐 Проверка языка ответов модели.
- 👤 Индивидуальные пользовательские профили.
- 🧠 Сохранение истории диалогов.
- 🎭 Настройка роли и стиля общения.
- 🔄 Сброс истории и профиля.

## 🧠 Используемая модель

Основная модель проекта:

**Qwen2.5-0.5B-Instruct**

Модель запускается локально через `llama.cpp` и предоставляет API, совместимый с форматом OpenAI Chat Completions.

## 🛠️ Технологии

- Python
- python-telegram-bot
- SQLite
- llama.cpp
- Qwen2.5-0.5B-Instruct
- Requests
- python-dotenv

## 📋 Команды бота

| Команда | Назначение |
|---|---|
| `/start` | Приветствие |
| `/help` | Список возможностей |
| `/reset` | Очистка истории |
| `/setuser` | Настройка профиля |
| `/myprofile` | Просмотр профиля |
| `/resetprofile` | Сброс профиля |
| `/cancel` | Отмена настройки |

## ⚙️ Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/Blatmetro/BlatmetroSecretary.git
cd BlatmetroSecretary
```

### 2. Создание виртуального окружения

```bash
python -m venv .venv
```

Активация в Windows:

```powershell
.venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка конфигурации

Создай файл `.env` на основе `.env.example` и укажи параметры:

```env
TELEGRAM_BOT_TOKEN=ТВОЙ_ТОКЕН_БОТА

MODEL_URL=http://127.0.0.1:9931/v1/chat/completions
MODEL_NAME=local-model

MAX_HISTORY_MESSAGES=8
MAX_REPLY_TOKENS=160
```

### 5. Запуск

Перед запуском бота необходимо запустить сервер языковой модели.

Затем выполни:

```bash
python bot.py
```

## 📁 Структура проекта

```text
BlatmetroSecretary/
├── data/
│   └── .gitkeep
├── tests/
│   └── test_language_validation.py
├── .env.example
├── .gitignore
├── bot.py
├── README.md
├── requirements.txt
└── run_bot.bat
```

## 🔒 Безопасность

- Не публикуйте Telegram-токены.
- Не загружайте `.env` в GitHub.
- Пользовательские данные и историю переписки храните локально.
- Не публикуйте базы данных и личную информацию пользователей.

## 📌 Версия проекта

**Текущая версия:** 0.2.0

**Дата обновления:** 26 ноября 2026 года.

## 👨‍💻 Разработчик

**Blatmetro**

Проект создан с помощью ChatGPT и OpenAI Codex.

---

*Blatmetro Secretary — ваш персональный ИИ-секретарь в Telegram.*
