# ARC Discord Assistant
[![Discord](https://img.shields.io/discord/868977679590883420)](https://discord.gg/xPJfDaztvS)

Manages Purdue ARC's discord server by providing:
- Google Calendar reminders
- Email domain verification
- Internal currency
- And more!

Built from [kkrypt0nn's template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template).

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
| smtp_server        | Domain of smtp server for outgoing emails.                            |
| smtp_port          | Port to use of smtp server.                                           |
| smtp_user          | Email authentication and outgoing address for smtp server.            |
| smtp_password      | Password authentication for smtp server.                              |
| reminder_channels  | IDs of channels to send Google Calendar reminders in                  |
| google_service     | Google service account JSON                                           |
| google_calendar_id | Google Calendar ID to source reminders                                |

<br />

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

| Command            | Definition                                                            |
| ------------------ | ----------------------------------------------------------------------|
| `.status`          | Prints general status information.                                    |
| `.poll <title>`    | Creates simple three option poll.                                     |
| `.8ball`           | Makes a practical decision.                                           |
| `.create_role_menu <title> <role_1>\|<emoji_1>,...` | Creates and prints a new role menu.                |

### Calendar

| Command              | Definition                                                          |
| -------------------- | --------------------------------------------------------------------|
| `.day` | Prints a list of scheduled events for the current day.              |
| `.week`  | Prints a list of scheduled events for the current week.             |


### Currency

| Command              | Definition                                                          |
| -------------------- | --------------------------------------------------------------------|
| `.thanks <member>`   | Grants member a single ARC coin.                                    |
| `.balance`           | Prints current balance of ARC coins.                                |
| `.leaderboard`       | Prints the 5 richest members.                                       |
| `.set <member> <amt>`| Sets amount of member's account (ADMIN ONLY)                        |

### Domain Verification

| Command              | Definition                                                          |
| -------------------- | --------------------------------------------------------------------|
| `.verify`            | DMs user to verify email address is under Purdue domain.            |
| `.clear`             | Deletes cached verification information. (ADMIN ONLY)               |

## Development
If you plan on performing local development, ensure you disconnect `config.json` from Git tracking:

```bash
git update-index --skip-worktree config.json
```

There is tons of drama becasue Discord is moving to a Slash command approach and the primary maintainer of Discord.py refuses to adhere to these changes. At some point, likely near April 2022, we will need to solve that transition. More information: https://gist.github.com/Rapptz/4a2f62751b9600a31a0d3c78100287f1


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details
