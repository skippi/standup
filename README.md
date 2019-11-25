# standup

[![Build Status](https://travis-ci.com/skippi/standup.svg?branch=master)](https://travis-ci.com/skippi/standup)
[![Join Discord](https://img.shields.io/badge/discord-join-7289DA.svg)](https://discord.gg/programming)

Discord bot for conducting standups in "The Programming Hangout".

## Installation

```bash
# Docker
docker build -t standup .
docker run --name standup --env STANDUP_BOT_TOKEN="MY_TOKEN" standup

# Dockerless
poetry install
STANDUP_BOT_TOKEN="MY_TOKEN" standup

# Development
poetry shell
STANDUP_BOT_TOKEN="MY_TOKEN"
poetry run standup
```

## User Guide

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
