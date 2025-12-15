#!/bin/bash

# FormatLab Studio - Push to GitHub
# Run this script to push the repository to GitHub

echo "🚀 FormatLab Studio - Pushing to GitHub"
echo "Username: rkabota"
echo "Repository: formatlab-studio"
echo ""

# Verify remote
echo "Checking remote..."
git remote -v
echo ""

# Push to main branch
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Push complete!"
echo ""
echo "Your repository is now at:"
echo "https://github.com/rkabota/formatlab-studio"
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/rkabota/formatlab-studio"
echo "2. Copy the Lovable prompt from LOVABLE_PROMPT_COPY_PASTE.md"
echo "3. Paste into Lovable Cloud to generate the frontend"
echo "4. Share the Lovable output result here"
