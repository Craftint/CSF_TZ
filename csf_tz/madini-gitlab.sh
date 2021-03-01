#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Specify the comment for updating GitLab. e.g. $0 'This update is for'"
    exit 1
fi

bench --site madini.aakvatech.com export-fixtures

vi apps/madini/madini/__init__.py
cd apps/madini
git add .
git commit -m "$1"
git push upstream master

