#!/usr/bin/env bash
#launcher script
python3 App/main.py &
python3 Telegram/WsTg.py &
python3 Telegram/TgBot.py &
python3 Camera/WsCam.py &
python3 Motor/WsMotor.py &
