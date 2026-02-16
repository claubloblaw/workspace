#!/bin/bash
# Run all Calgary Tools projects

echo "🚀 Running all 22 Calgary Tools projects..."
echo "================================================"

for i in {01..22}; do
    dir=$(ls -d ${i}-* 2>/dev/null | head -1)
    if [ -d "$dir" ]; then
        echo ""
        echo "▶️  Running $dir..."
        (cd "$dir" && python3 main.py 2>&1 | tail -20)
        echo "✅ Completed $dir"
    fi
done

echo ""
echo "================================================"
echo "🎉 All projects complete!"
echo ""
echo "📊 Generating summary..."
find . -name "*.json" -o -name "*.csv" -o -name "*.html" | wc -l | xargs echo "   Output files created:"
