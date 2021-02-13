#!/bin/bash

# Add to the crontab:
# * * * * * cd /my/path/lattice-surgery-compiler/webgui && ./call_deploy.sh

DEPLOY_BRANCH=webgui-deploy
SERVER_PID_FILE=server_pid
DEPLOY_LOG=deploy.log

git fetch origin webgui-deploy
new_commits=$(git log HEAD..origin/$DEPLOY_BRANCH --oneline)
if [ -n "$new_commits" ]
then
  echo "================ [`date`] running $0 ================ " >> $DEPLOY_LOG
  echo "New commits:" >> $DEPLOY_LOG
  echo "$new_commits" >> $DEPLOY_LOG
  echo "Killing server." >> $DEPLOY_LOG
  kill "$(cat $SERVER_PID_FILE)"
  echo "Resetting git." >> $DEPLOY_LOG
  git reset --hard origin/$DEPLOY_BRANCH
  echo "Running deploy script." >> $DEPLOY_LOG
  ./deploy.sh 2>&1 | tee -a $DEPLOY_LOG
  echo "================ [`date`] Back to $0 ================ " >> $DEPLOY_LOG
  echo "Starting the server." >> $DEPLOY_LOG
  PYTHONPATH="..:$PYTHONPATH" python serve.py &
  echo $! > $SERVER_PID_FILE
  echo "Server started with pid $(cat $SERVER_PID_FILE)." >> $DEPLOY_LOG
  echo "================ [`date`] Done running $0 ================ " >> $DEPLOY_LOG
fi
