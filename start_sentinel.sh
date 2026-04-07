#!/bin/bash

# Sentinel Hook — Automated Start Script (Cross-Platform)
# Her sistemde (macOS, Linux, Windows/Git Bash) çalışacak şekilde uyarlandı.

# Betiğin bulunduğu dizini al
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🚀 Initiating Sentinel Hook Subsystems from $PROJECT_ROOT..."

# Kapatma (Ctrl+C) yakalayıcısı: Script kapatıldığında arka plandaki tüm işlemleri temizle
trap 'echo -e "\n🛑 Sistemler kapatılıyor... Bizi tercih ettiğiniz için teşekkürler!"; kill 0' SIGINT SIGTERM EXIT

# 1. Rust Backend'i arka planda başlat (&)
echo "✅ [SERVICE 1] Rust Backend (Axum/WebSocket) is spinning up..."
(cd "$PROJECT_ROOT/sentinel-rust" && source ../.venv/bin/activate && cargo run) &

sleep 1

# 2. React Tactical Dashboard'u arka planda başlat (&)
echo "✅ [SERVICE 2] React Dashboard (Vite/React) is spinning up..."
(cd "$PROJECT_ROOT/web_ui" && npm run dev) &

echo ""
echo "--------------------------------------------------"
echo "📱 REMINDER: Launch the DummyBank iOS app via Xcode (⌘R)."
echo "🔗 ACCESS DASHBOARD: http://localhost:5173"
echo "🛑 TO STOP ALL SERVICES: Press CTRL + C"
echo "--------------------------------------------------"

# Arka plandaki işlemlerin kapanmasını bekle (Betiği ayakta tutar)
wait