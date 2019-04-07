#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Specify the comment for updating GitLab. e.g. $0 'This update is for'"
    exit 1
fi

vi apps/fmlms/fmlms/__init__.py
bench --site gsl5299.aakvatech.com export-fixtures
cd apps/fmlms
git add .
git commit -m "$1"
git push upstream master

