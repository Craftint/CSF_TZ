#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Specify the comment for updating GitLab. e.g. $0 'This update is for'"
    exit 1
fi

vi apps/grantsms/grantsms/__init__.py
bench --site dev-stcl.kuungatech.com export-fixtures
cd apps/grantsms
git add .
git commit -m "$1"
git push upstream master

