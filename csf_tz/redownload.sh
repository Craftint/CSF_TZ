#!/bin/bash

cd apps/$1
git stash; git fetch --all; git pull
