#!/bin/bash

echo "=========================================="
echo "Chat Feature UI Test"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found"
    echo "Using system Python..."
fi

echo ""
echo "Running chat UI test..."
echo ""

python3 test_chat_ui.py

echo ""
echo "Test completed!"
