#!/bin/sh

echo ""
echo 'Creating python virtual environment ".venv"'
echo ""
cd ./backend
python3 -m venv .venv

echo ""
echo "Restoring backend python packages"
echo ""
./.venv/bin/python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to restore backend python packages"
    exit $?
fi

echo ""
echo "Restoring frontend npm packages"
echo ""
cd ../frontend
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
echo "Starting backend"
echo ""
cd ../backend
./.venv/bin/python app.py --reload
if [ $? -ne 0 ]; then
    echo "Failed to start backend"
    exit $?
fi
