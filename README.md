# ARC Discord Assistant
[![Discord](https://img.shields.io/discord/868977679590883420)](https://discord.gg/xPJfDaztvS)

Helps Purdue ARC run our Discord server.

Derived from [kkrypt0nn's template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template).

## Setup

Invite your bot on servers using the following invite:
https://discordapp.com/oauth2/authorize?&client_id=YOUR_APPLICATION_ID_HERE&scope=bot&permissions=8 

Configuration handled in `config.json`:

| Variable                  | What it is                                                            |
| ------------------------- | ----------------------------------------------------------------------|
| YOUR_BOT_PREFIX_HERE      | The prefix(es) of your bot                                            |
| YOUR_BOT_TOKEN_HERE       | The token of your bot                                                 |
| YOUR_APPLICATION_ID_HERE  | The application ID of your bot                                        |
| OWNERS                    | The user ID of all the bot owners                                     |

In the [blacklist](blacklist.json) file you now can add IDs (as integers) in the `ids` list.

### OLD:
Add app to Heroku, then configure scheduled run of the following command:

```bash
python send_updates.py
```

The set schedule helps parametrize when updates are sent to discord.

`send_updates.py` is currently written to obtain daily events, so the command should be scheduled to run daily.

This application relies on four environment variables:

- `GOOGLE_SERVICE_ACCOUNT_JSON`: json string given by Google API service account
- `CALENDAR_ID`: ID for respective Google Calendar
- `DISCORD_TOKEN`: bot token given by Discord
- `REDIS_URL`: URL for Redis file store (provided by Redis Heroku application)

### END OLD

Before running the bot you will need to install all the requirements with this command:

```
pip install -r requirements.txt
```

Then you can run:

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
