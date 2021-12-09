#!/bin/bash
# description "Start Tmux"
/bin/sleep 1
# Create a new tmux session named bot..
/usr/bin/tmux kill-session -t bot
/bin/sleep 3
/usr/bin/tmux new-session -d -s bot
/bin/sleep 1
/usr/bin/tmux send-keys -t bot:0 "cd /home/ubuntu/HoshinoBot" C-m
/bin/sleep 1
/usr/bin/tmux send-keys -t bot:0 "sudo python3 run.py" C-m
/bin/sleep 1
