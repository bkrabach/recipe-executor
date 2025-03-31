#!/bin/bash
# Simple helper script to demonstrate the simplified CLI

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 \"Product description\" [input_dir] [output_dir]"
    exit 1
fi

DESC="$1"
INPUT_DIR="${2:-.}"  # Default to current directory if not provided
OUTPUT_DIR="${3:-./output}"  # Default to ./output if not provided

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

echo "🚀 Creating project based on: $DESC"
echo "📂 Input directory: $INPUT_DIR"
echo "📁 Output directory: $OUTPUT_DIR"
echo "⏳ Processing..."

# Execute recipe with the provided parameters
python recipe_executor/main.py recipes/recipe_executor/create.json "$DESC" -i "$INPUT_DIR" -o "$OUTPUT_DIR"

echo "✅ Done! Generated files are in $OUTPUT_DIR"