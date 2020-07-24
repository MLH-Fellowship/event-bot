# Session Bot

Discord bot that announces upcoming sessions on the Additional Fun & Educational Events calendar!

Inspired by the [Hack Quarantine](https://hackquarantine.com) [Calendar Bot](https://github.com/HackQuarantine/calendar-bot) used to automatically make announcements from their calendar.

![Example](img/example.png)

![Docker Image CI](https://github.com/MLH-Fellowship/session-bot/workflows/Docker%20Image%20CI/badge.svg)

![Deploying to Google Compute Engine](https://github.com/MLH-Fellowship/session-bot/workflows/Deploying%20to%20Google%20Compute%20Engine/badge.svg)

## Setup

Make sure to set your Google Calendar to the same timezone as the Discord Bot. In this case, it's the timezone of the Compute Engine on Google Cloud.

```
docker build -t session-bot .
cp example.env .env
```

_Make sure to fill the `.env` file with the required fields_

## Run

```
docker run --name session-bot --env-file .env -d session-bot
```

Alternatively build and run with `docker-compose`:

```bash
docker-compose build
docker-compose up -d
docker-compose logs -f
```
