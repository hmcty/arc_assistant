# ARC Discord Assistant
[![Discord](https://img.shields.io/discord/868977679590883420)](https://discord.gg/xPJfDaztvS)

Helps Purdue ARC run our Discord server.

Derived from [kkrypt0nn's template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template).

## Setup

Invite your bot on servers using the following invite:
https://discordapp.com/oauth2/authorize?&client_id=YOUR_APPLICATION_ID_HERE&scope=bot&permissions=8

Configuration handled in `config.json`:

| Variable           | Definition                                                            |
| ------------------ | ----------------------------------------------------------------------|
| bot_prefix         | Indicator of a bot command (default: ".")                             |
| bot_token          | Discord token application                                             |
| server_id          | Server ID where bot instance lives                                    |
| owners             | The user ID of all the bot owners                                     |
| db                 | Database file location (default: "./bot.db)                           |
| sendgrid_email     | Sendgrid email account                                                |
| sendgrid_api_key   | Sendgrid API key                                                      |
| google_service     | Google service account JSON                                           |
| google_calendar_id | Google Calendar ID to source reminders                                |

Before running the bot, install required dependencies:

```
pip install -r requirements.txt
```

Then start the bot using the following command:

```
python3.8 bot.py
```

## Commands

### General
```
.status
```
Prints general status information.

```
.poll <title>
```
Creates simple three option poll.

```
.8ball
```
Makes a practical decision.

```
.create_role_menu emoji_1 role_1...
```
Creates and prints a new role menu.

### Calendar
```
.get_todays_events
```
Prints a list of scheduled events for the current day.

```
.get_weeks_events
```
Prints a list of scheduled events for the current week.

### Currency
```
.thanks <user>
```
Grants member a single ARC coin.

```
.balance
```
Prints current balance of ARC coins.

```
.leaderboard
```
Prints top 5 members with most amount of ARC coins.

### Domain Verification
```
.verify
```
DMs user to verify email address is under Purdue domain.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details


**ARC Assistant** handles a variety of functions on the ARC discord channel such as:
- Verifying student emails
- Posting upcoming events
- Gifting ARC coins

[![Discord](https://img.shields.io/discord/868977679590883420)](https://discord.gg/xPJfDaztvS)
