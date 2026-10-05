# Circlechek

**Русский** · [English](README.en.md)

[![CI](https://github.com/EDeev/circlechek/actions/workflows/ci.yml/badge.svg)](https://github.com/EDeev/circlechek/actions/workflows/ci.yml)
[![Docker](https://github.com/EDeev/circlechek/actions/workflows/docker.yml/badge.svg)](https://github.com/EDeev/circlechek/actions/workflows/docker.yml)
[![License](https://img.shields.io/github/license/EDeev/circlechek)](LICENSE)

Telegram-бот для кружочков: делает из квадратного видео видеосообщение-кружок, а из присланного
кружочка — обычное видео, где углы заполнены размытым кадром или градиентом под цвет картинки.

**Статус:** личный проект, завершён · бот [@circlechek_bot](https://t.me/circlechek_bot)

![Кружочек и два варианта фона](docs/demo.png)

**Стек:** Python 3.12 · aiogram 3 · MoviePy 2 · Pillow · NumPy · Docker

## Возможности

- **Видео → кружочек.** Квадратное видео до минуты возвращается кружком.
- **Кружочек → видео.** Бот разбирает кружок на кадры, заполняет углы и собирает видео обратно со звуком.
  Фон на выбор:
  - **блюр** — размытая центральная часть кадра;
  - **градиент** — по среднему цвету кадра.
- Тяжёлая обработка идёт в отдельном потоке, поэтому пока один кружочек обрабатывается, бот отвечает
  остальным. Каждая обработка — в своей временной папке, которая убирается и при ошибке.

> [!NOTE]
> У части кружочков Telegram бывают некорректные метаданные — тогда обработка не удастся или в видео
> будет брак. Бот предупреждает об этом, результат стоит проверять.

## Запуск

```bash
git clone https://github.com/EDeev/circlechek.git && cd circlechek
cp .env.example .env      # BOT_TOKEN от @BotFather
docker compose up -d
```

Готовый образ: `docker pull ghcr.io/edeev/circlechek` или `docker pull dcr.deev.su/edeev/circlechek`.

Без Docker: Python 3.12, `pip install -r requirements.txt`, затем `cd code && BOT_TOKEN=… python bot.py`
(FFmpeg ставится вместе с MoviePy).

## Структура

```
code/bot.py         запуск
code/handlers.py    команды, приём видео и кружочков, кнопки выбора фона
code/scripts.py     Movie — кадры и звук через MoviePy; Frame — фон и маска-круг через Pillow и NumPy
data/               временные файлы обработки
```

## Разработка

```bash
pip install ruff -r requirements.txt
ruff check --select E9,F code
```

CI на каждый push проверяет код и прогоняет обработку тестовых кружочков (со звуком и без, оба вида
фона). Docker-образ собирается по тегу `v*` и публикуется в GitHub Packages и `dcr.deev.su`.

## Лицензия

MIT — см. [LICENSE](LICENSE).

## Автор

**Деев Егор Викторович** — [GitHub](https://github.com/EDeev) · [Telegram](https://t.me/DeevEgor) · [egor@deev.space](mailto:egor@deev.space)

---

<div align="center">
  <sub>⭐ Если проект оказался полезным, поставьте звёздочку на GitHub!</sub>
  <p><sub>Сделано с ❤️ — <a href="https://deev.space">deev.space</a></sub></p>
</div>
