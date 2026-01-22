#!/bin/bash
# Quick syntax check for all Python files

echo "🔍 Checking Python syntax..."

errors=0

for file in *.py; do
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo "✅ $file"
        else
            echo "❌ $file - SYNTAX ERROR"
            python3 -m py_compile "$file"
            errors=$((errors + 1))
        fi
    fi
done

if [ $errors -eq 0 ]; then
    echo ""
    echo "✅ All files passed syntax check!"
    exit 0
else
    echo ""
    echo "❌ $errors file(s) have syntax errors"
    exit 1
fi
