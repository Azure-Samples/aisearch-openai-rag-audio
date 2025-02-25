#!/bin/sh

. ./scripts/load_python_env.sh

echo ""
echo "Starting backend"
echo ""
pwd
ls
./.venv/bin/python app/backend/app_api.py
if [ $? -ne 0 ]; then
    echo "Failed to start backend"
    exit $?
fi
