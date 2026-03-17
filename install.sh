#!/bin/bash
# =============================================================
# Sentinel Hook - Otomatik Kurulum Scripti (install.sh)
# Kullanım: bash install.sh
# Açıklama: Tüm bağımlılıkları (Frida, Python Sanal Ortam, Araçlar)
#           tek seferde kurar ve hazır hale getirir.
# =============================================================

set -e  # Herhangi bir hata olursa dur

# Renkli çıktı için
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo ""
echo -e "${GREEN}██████████████████████████████████████████${RESET}"
echo -e "${GREEN}   🛡️  SENTINEL HOOK - KURULUM BAŞLIYOR  ${RESET}"
echo -e "${GREEN}██████████████████████████████████████████${RESET}"
echo ""

# -------------------------------------------------------
# 1. ADIM: Python 3 kontrolü
# -------------------------------------------------------
echo -e "${YELLOW}[1/5] Python 3 kontrol ediliyor...${RESET}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[HATA] Python 3 bulunamadı. Lütfen önce Python 3.10+ kurun.${RESET}"
    echo "       macOS için: brew install python"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[✓] Python ${PYTHON_VERSION} bulundu.${RESET}"

# -------------------------------------------------------
# 2. ADIM: Sanal ortam (Virtual Environment) kurulumu
# -------------------------------------------------------
echo ""
echo -e "${YELLOW}[2/5] Python sanal ortamı (.venv) oluşturuluyor...${RESET}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}[✓] .venv oluşturuldu.${RESET}"
else
    echo -e "${GREEN}[✓] .venv zaten mevcut, atlanıyor.${RESET}"
fi
source .venv/bin/activate

# -------------------------------------------------------
# 3. ADIM: pip güncelleme
# -------------------------------------------------------
echo ""
echo -e "${YELLOW}[3/5] pip güncelleniyor...${RESET}"
pip install --upgrade pip --quiet
echo -e "${GREEN}[✓] pip güncellendi.${RESET}"

# -------------------------------------------------------
# 4. ADIM: requirements.txt bağımlılıklarını yükle
# -------------------------------------------------------
echo ""
echo -e "${YELLOW}[4/5] Frida ve bağımlılıklar yükleniyor (requirements.txt)...${RESET}"
pip install -r requirements.txt
echo -e "${GREEN}[✓] Tüm bağımlılıklar yüklendi.${RESET}"

# -------------------------------------------------------
# 5. ADIM: Frida kurulumu doğrulama
# -------------------------------------------------------
echo ""
echo -e "${YELLOW}[5/5] Frida kurulumu doğrulanıyor...${RESET}"
if command -v frida &>/dev/null; then
    FRIDA_VERSION=$(frida --version 2>&1)
    echo -e "${GREEN}[✓] Frida ${FRIDA_VERSION} başarıyla kuruldu!${RESET}"
else
    echo -e "${RED}[HATA] Frida kurulu görünmüyor. Sanal ortamın aktif olduğundan emin ol:${RESET}"
    echo "       source .venv/bin/activate"
fi

# -------------------------------------------------------
# 6. ADIM: Yeni dökümantasyon dosyalarını Git'e commit et
# -------------------------------------------------------
echo ""
echo -e "${YELLOW}[6/6] Proje dosyaları Git'e kaydediliyor...${RESET}"
if git rev-parse --is-inside-work-tree &>/dev/null; then
    git add \
        README.md \
        ROADMAP.md \
        USAGE.md \
        DISCLAIMER.md \
        CONTRIBUTING.md \
        CHANGELOG.md \
        SECURITY.md \
        requirements.txt \
        install.sh \
        src/hooks/ 2>/dev/null || true

    # Eğer commit edilecek değişiklik varsa commit at
    if ! git diff --cached --quiet; then
        git commit -m "docs: proje dökümantasyonu ve klasör yapısı eklendi

- README, ROADMAP, USAGE, DISCLAIMER, CONTRIBUTING, CHANGELOG, SECURITY eklendi
- install.sh ve requirements.txt otomatik kurulum dosyaları eklendi
- src/hooks/ klasörleri 01_biometrics / 02_camera / 03_ml_vision / 04_anti_tamper olarak düzenlendi"
        echo -e "${GREEN}[✓] Git commit başarılı!${RESET}"
    else
        echo -e "${GREEN}[✓] Commit edilecek yeni değişiklik yok, atlanıyor.${RESET}"
    fi
else
    echo -e "${RED}[-] Bu dizin bir Git reposu değil. Commit atlanıyor.${RESET}"
fi

# -------------------------------------------------------
# ÖZET
# -------------------------------------------------------
echo ""
echo -e "${GREEN}══════════════════════════════════════════════${RESET}"
echo -e "${GREEN}  ✅  KURULUM TAMAMLANDI!                     ${RESET}"
echo -e "${GREEN}══════════════════════════════════════════════${RESET}"
echo ""
echo -e "  Sanal ortamı aktive et:"
echo -e "  ${YELLOW}source .venv/bin/activate${RESET}"
echo ""
echo -e "  Bağlı cihazları listele:"
echo -e "  ${YELLOW}frida-ps -Uai${RESET}"
echo ""
echo -e "  Örnek bypass çalıştır:"
echo -e "  ${YELLOW}frida -U -n DummyBank -l src/hooks/04_anti_tamper/root_jailbreak_bypass.js${RESET}"
echo ""
