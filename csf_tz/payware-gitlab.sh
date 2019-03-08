#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Specify the comment for updating GitLab. e.g. $0 'This update is for'"
    exit 1
fi


vi apps/payware/payware/__init__.py
bench --site demo.payware.co.tz export-fixtures
cd apps/payware
git add .
git commit -m "$1"
git push upstream master

