# standup

[![Build Status](https://travis-ci.com/skippi/standup.svg?branch=master)](https://travis-ci.com/skippi/standup)
[![Join Discord](https://discordapp.com/api/guilds/244230771232079873/embed.png)](https://discord.gg/programming)

Discord bot for conducting standups in "The Programming Hangout".

## Installation

```bash
# Docker
docker build -t standup .
docker run --name standup --env STANDUP_BOT_TOKEN="MY_TOKEN" standup

# Dockerless
poetry install
standup "MY_TOKEN"
```

### Docker Configuration

There are two important options to configure during image creation:

- Discord API token
- Volume mount

We can configure the token by passing it as an environment variable
`STANDUP_BOT_TOKEN`. To configure volumes, mount to `/data/`. This is because
the default Dockerfile persists all data to `/data/standup.db`. The following
example depicts both of these options.

```bash
docker build -t "standup-img" .
docker run --name "my-standup-container" \
--env STANDUP_BOT_TOKEN="MY_TOKEN" \
--mount source=standup-volume,target=/data "standup-img"
```

### Dockerless Configuration

We can use `standup --help` to check the possible configuration options for the
`standup` script. Among these include database customization.

```bash
standup --database "./data/custom_database.db" "MY_TOKEN"
```

## User Guide

### Required Permissions

- `MANAGE_ROLES`
- `VIEW_CHANNEL`
- `SEND_MESSAGES`
- `MANAGE_MESSAGES`
- `READ_MESSAGE_HISTORY`
- `ADD_REACTIONS`
- `EMBED_LINKS`

### Configuration

This bot contains the following features:

- Allows delegating channels as "standup rooms".
- All message posts in the standup room must conform to the "standup format".
- Upon successfully posting, this bot assigns the author a customizable set of roles.
  These roles are removed from the user after a 24 hour period.

Knowing this, we'll need to configure our channels and roles. These next steps
require the `ADMINISTRATOR` permission.

Let's start with the channels. In this example, we'll configure the channel with id
648308883898499072 to be a room. We'll then list out the rooms to verify our
configuration.

```txt
@standup-bot rooms add 648308883898499072
@standup-bot rooms list

1: 648308883898499072 | Roles: {}
```

Finally, we'll need to add what roles we want to assign per standup post.
This is done by setting the `roles` key to a comma separated list of role ids.

```txt
@standup-bot rooms config 648308883898499072 roles 648395618359967744,6483956183512382382
@standup-bot rooms list

1: 648308883898499072 | Roles: {648395618359967744, 6483956183512382382}
```

## Developer Guide

Please read the [contributing guidelines](./CONTRIBUTING.md).
