#!/bin/bash

# Inbox that receives Problem of the Day
export BENSONBOT_EMAIL_ADDRESS="example@example.com"
export BENSONBOT_EMAIL_PASSWORD=""

# Discord token
export BENSONBOT_DISCORD_TOKEN=""

# Tokens for HTML/CSS to Image API (htmlcsstoimage.com)
export BENSONBOT_HCTI_USER=""
export BENSONBOT_HCTI_TOKEN=""

# Env type determines which cogs are loaded
export BENSONBOT_ENV_TYPE=""

python3.7 main.py
