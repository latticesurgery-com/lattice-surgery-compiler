#!/bin/bash

DEPLOY_BRANCH=webgui-deploy

git fetch origin webgui-deploy
new_commits=$(git log HEAD..origin/$DEPLOY_BRANCH --oneline)
if [ -n "$new_commits" ]
then
  git reset --hard origin/$DEPLOY_BRANCH
  ./deploy.sh 2>&1 | tee -a deploy.log
fi