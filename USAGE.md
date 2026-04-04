<div align="center">

# 📖 USAGE — Kullanım Rehberi

### Sentinel Hook · Test ve Operasyon El Kitabı

[![Frida](https://img.shields.io/badge/Frida-17.9.1-00C9FF?style=for-the-badge&logo=python&logoColor=white)](https://frida.re)
[![iOS](https://img.shields.io/badge/iOS-16%2B-black?style=for-the-badge&logo=apple)](https://developer.apple.com)
[![Android](https://img.shields.io/badge/Android-11%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com)

</div>

---

## 📂 Modül Haritası

```
src/hooks/
├── 01_biometrics/       ← Phase 2: FaceID / BiometricPrompt kırıcılar
├── 02_camera/           ← Phase 3: Kamera sensörü spoofing
├── 03_ml_vision/        ← Phase 4: Yapay Zeka / ML blindspot
└── 04_anti_tamper/      ← Phase 5: Görünmezlik duvarı
```

---

## 🔬 Hazırlık: Cihazı Frida'ya Tanıtmak

Testlere başlamadan önce Frida'nın cihazı gördüğünden emin olun:

```bash
# Sanal ortamı aktive et
source .venv/bin/activate

# Bağlı cihaz uygulamalarını listele
frida-ps -Uai
```

Çıktıda `DummyBank` (veya hedef uygulamanın adı/ID'si) görünmelidir.

---

## 🔥 Modül Bazlı Test Senaryoları

### 📦 Bölüm 1 — Biyometrik Bypass `01_biometrics/`

**Amaç:** Face ID / Parmak İzi eşleşmesi olmadan `"Kimlik Doğrulandı"` yanıtı almak.

```bash
frida -U -n DummyBank -l src/hooks/01_biometrics/local_auth_bypass.js
```

**Beklenen Terminal Çıktısı:**
```
[🌟] SENTINEL: Biyometrik Bypass Aktif
[+] evaluatePolicy hooked → return TRUE forced
[💥] Kimlik doğrulama başarılı (Bypass)!
```

> [!TIP]
> Ardından cihaz ekranında **"Face ID ile Giriş Yap"** tuşuna basın. Donanım okumadan kapı açılacaktır.

---

### 📦 Bölüm 2 — Kamera Bypass `02_camera/`

**Amaç:** Liveness kamerasına sahte statik bir resim (`hacker.jpg`) yerleştirmek.

```bash
# Önce test yüzünü yerleştir
cp /path/to/yuz.jpg .local/test-faces/hacker.jpg

# Hook'u enjekte et
frida -U -n DummyBank -l src/hooks/02_camera/camera_bypass.js
```

**Beklenen Terminal Çıktısı:**
```
[🌟] SENTINEL HOOK: Kamera Bypass Aktif Ediliyor...
[💥] SENTINEL YAKALADI: Sensörden Veri Akışı Geldi!
[Aksiyon]: SAHTE YÜZ ENJEKTİ EDİLDİ -> Liveness Kontrolüne Yollandı!
```

---

### 📦 Bölüm 3 — AI / ML Bypass `03_ml_vision/`

**Amaç:** Karanlık / boş bir karede bile **"Canlı İnsan Yüzü"** onayı verdirmek.

```bash
frida -U -n DummyBank -l src/hooks/03_ml_vision/vision_bypass.js
```

**Beklenen Terminal Çıktısı:**
```
[+] HEDEF AI MOTORU BULUNDU: VNDetectFaceRectanglesRequest
[💥] SENTINEL: AI Kandırıldı! 'Canlı Yüz' Onayı Verildi!
```

> [!NOTE]
> Telefonu yüzüstü kapatın (tamamen karanlık kamera) ve butona basın. Yine de onay verecektir.

---

### 📦 Bölüm 4 — Anti-Tamper Bypass `04_anti_tamper/`

**Amaç:** Uygulamanın **"Cihaz Jailbreak'li!"** diyerek kendini kapatmasını engellemek.

```bash
# -f: Uygulamayı Frida başlatsın (ilk satırdan hook alsın)
frida -U -f com.dummy.bank -l src/hooks/04_anti_tamper/root_jailbreak_bypass.js
```

**Beklenen Terminal Çıktısı:**
```
[🌟] SENTINEL HOOK: Root & Jailbreak Bypass Aktif Ediliyor...
[+] Objective-C 'NSFileManager.fileExistsAtPath' kancalandı.
[💥] SENTINEL GİZLENİYOR: Uygulama yasaklı dosya aradı (/Applications/Cydia.app)
```

---

## 🔗 ALL-IN-ONE: Tüm Silahları Birden Ateşlemek

Gerçek test senaryolarında tüm modüller aynı anda çalışmalıdır:

```bash
frida -U -n DummyBank \
    -l src/hooks/04_anti_tamper/root_jailbreak_bypass.js \
    -l src/hooks/04_anti_tamper/ssl_pinning_bypass.js \
    -l src/hooks/02_camera/camera_bypass.js \
    -l src/hooks/03_ml_vision/vision_bypass.js \
    -l src/hooks/01_biometrics/local_auth_bypass.js
```

> [!IMPORTANT]
> `04_anti_tamper` modülleri **her zaman ilk sıraya** alınmalıdır. Görünmezlik duvarı devreye girmeden diğer hook'lar tespit edilebilir.
