#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Specify the comment for updating GitLab. e.g. $0 'This update is for'"
    exit 1
fi

bench --site dev-csf-tz.aakvatech.com export-fixtures

vi apps/csf_tz/csf_tz/__init__.py
cp *sh apps/csf_tz/csf_tz
cd apps/csf_tz
git add .
git commit -m "$1"
git push upstream master

