#!/bin/bash

echo ""
echo "Restoring frontend npm packages"
echo ""
cd app/frontend
npm install
if [ $? -ne 0 ]; then
    echo "Failed to restore frontend npm packages"
    exit $?
fi

echo ""
echo "Building frontend"
echo ""
npm run build
if [ $? -ne 0 ]; then
    echo "Failed to build frontend"
    exit $?
fi

echo ""
echo "Restoring backend python packages"
echo ""
cd ../../
pip install -r app/backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to restore backend python packages"
    exit $?
fi

echo ""
echo "Starting backend"
echo ""
python app/backend/app.py
if [ $? -ne 0 ]; then
    echo "Failed to start backend"
    exit $?
fi
