#!/bin/bash

# Sentinel Hook — Automated Start Script (macOS)
# This script opens two new terminal tabs to run the Backend and Frontend concurrently.

PROJECT_ROOT=$(pwd)

echo "🚀 Initiating Sentinel Hook Subsystems..."

# Tab 1: Rust Backend orchestration server
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_ROOT/sentinel-rust' && source ../.venv/bin/activate && cargo run\""
echo "✅ [TAB 1] Rust Backend (Axum/WebSocket) is spinning up..."

# Tab 2: React Tactical Dashboard
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_ROOT/web_ui' && npm run dev\""
echo "✅ [TAB 2] React Dashboard (Vite/React) is spinning up..."

echo ""
echo "--------------------------------------------------"
echo "📱 REMINDER: Launch the DummyBank iOS app via Xcode (⌘R)."
echo "🔗 ACCESS DASHBOARD: http://localhost:5173"
echo "--------------------------------------------------"
