#!/bin/sh

BOT_TOKEN=""
VOLUME_SOURCE="standup-volume"

docker build -t standup .
docker run --rm --name standup --env STANDUP_BOT_TOKEN=$BOT_TOKEN --mount source=$VOLUME_SOURCE,target=/data standup
