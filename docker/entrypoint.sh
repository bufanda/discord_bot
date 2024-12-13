#!/bin/sh
# Entrypoint for scum bot
#

chown -R scumbot /app
exec runuser -u scumbot -- "$@"
