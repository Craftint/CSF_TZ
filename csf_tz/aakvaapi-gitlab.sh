#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Specify the comment for updating GitLab. e.g. $0 'This update is for'"
    exit 1
fi

bench --site smsgw.aakvatech.com export-fixtures

vi apps/aakvaapi/aakvaapi/__init__.py
cd apps/aakvaapi
git add .
git commit -m "$1"
git push upstream master

