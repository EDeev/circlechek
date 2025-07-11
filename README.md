# 🎥 Circlechek

**Telegram-бот для преобразования квадратных видео в кружочки и обработки видеосообщений с настраиваемыми фонами.**

## 📋 Описание

Circlechek — это простой и функциональный Telegram-бот, предназначенный для работы с видеоконтентом. Бот предоставляет две основные возможности:

1. **Преобразование видео в кружочки** — превращает квадратные видео (до 1 минуты) в формат видеосообщений Telegram
2. **Обработка кружочков** — конвертирует видеосообщения в обычные видео с настраиваемым фоном по краям

## ✨ Функциональность

### 🔄 Видео → Кружочек
- Принимает квадратные видеофайлы длительностью до 60 секунд
- Автоматически преобразует их в формат кружочков Telegram
- Сохраняет качество и плавность воспроизведения

### 🎨 Кружочек → Видео
- Обрабатывает видеосообщения с добавлением фона по краям
- **Градиентный фон** — создает плавный цветовой переход на основе доминирующих цветов кадра
- **Размытый фон** — использует размытую версию центральной части видео
- Сохраняет исходное аудио и синхронизацию

## 🛠 Технологический стек

- **Python 3.x** — основной язык разработки
- **aiogram** — асинхронная библиотека для работы с Telegram Bot API
- **PIL (Pillow)** — обработка изображений и создание эффектов
- **MoviePy** — работа с видеофайлами, извлечение кадров и аудио
- **NumPy** — математические операции с массивами для обработки изображений

## 🚀 Установка и запуск

### Требования
- Python 3.8+
- Токен Telegram-бота от [@BotFather](https://t.me/BotFather)

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка
1. Получите токен бота в [@BotFather](https://t.me/BotFather)
2. Отредактируйте файл `code/config.py`:
```python
botToken = "ВАШ_ТОКЕН_БОТА"
```

### Запуск
```bash
cd code
python bot.py
```

## 📁 Структура проекта

```
circlechek/
├── code/
│   ├── bot.py          # Основной файл запуска бота
│   ├── handlers.py     # Обработчики команд и сообщений
│   ├── scripts.py      # Классы для работы с видео и изображениями
│   ├── config.py       # Конфигурация бота
│   └── init.py         # Инициализация бота и утилиты
├── data/
│   ├── circles/        # Временные файлы кружочков
│   ├── video_notes/    # Временные видеосообщения
│   └── videos/         # Обработанные видео
└── README.md
```

## 🎯 Использование

1. **Начало работы**: Отправьте `/start` боту
2. **Создание кружочка**: Отправьте квадратное видео (до 1 минуты)
3. **Обработка кружочка**: 
   - Отправьте видеосообщение боту
   - Выберите тип фона: "Градиент" или "Блюр"
   - Получите обработанное видео

## ⚠️ Важные особенности

- Видео для преобразования в кружочки должны быть **квадратными** и **не длиннее 1 минуты**
- Некоторые кружочки могут иметь некорректные метаданные, что может привести к ошибкам обработки
- Рекомендуется всегда проверять качество полученного результата
- Все временные файлы автоматически удаляются после обработки

## 📄 Лицензия

Проект распространяется под лицензией MIT.

## 👨‍💻 Автор

**Деев Егор Викторович** - Backend Developer  
- GitHub: [@EDeev](https://github.com/EDeev)
- Email: egor@deev.space
- Telegram: [@Egor_Deev](https://t.me/Egor_Deev)

---

<div align="center">
  <sub>⭐ Если проект оказался полезным, поставьте звездочку на GitHub!</sub>
  <p><sub>Создано с ❤️ от вашего дорогого - deev.space ©</sub></p>
</div>
