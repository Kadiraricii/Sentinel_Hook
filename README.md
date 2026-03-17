<div align="center">

```
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗          
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║          
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║          
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║          
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗     
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝    
                    H  O  O  K                                         
```

<h3>Advanced Dynamic Instrumentation Framework</h3>
<h4>Biometric · Liveness · AI/ML Security Bypass</h4>

---

[![Stars](https://img.shields.io/github/stars/Kadiraricii/Sentinel_Hook?style=for-the-badge&color=FFD700&logo=github&logoColor=white)](https://github.com/Kadiraricii/Sentinel_Hook/stargazers)
[![Forks](https://img.shields.io/github/forks/Kadiraricii/Sentinel_Hook?style=for-the-badge&color=00C9FF&logo=github&logoColor=white)](https://github.com/Kadiraricii/Sentinel_Hook/network/members)
[![Issues](https://img.shields.io/github/issues/Kadiraricii/Sentinel_Hook?style=for-the-badge&color=FF6B6B&logo=github&logoColor=white)](https://github.com/Kadiraricii/Sentinel_Hook/issues)
[![License](https://img.shields.io/badge/License-Educational%20Only-8A2BE2?style=for-the-badge&logo=bookstack&logoColor=white)](./DISCLAIMER.md)

[![Frida](https://img.shields.io/badge/Frida-17.9.1-00C9FF?style=for-the-badge&logo=python&logoColor=white)](https://frida.re)
[![iOS](https://img.shields.io/badge/iOS-16%2B-black?style=for-the-badge&logo=apple&logoColor=white)](https://developer.apple.com)
[![Android](https://img.shields.io/badge/Android-11%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com)
[![Swift](https://img.shields.io/badge/Swift-5.9-FA7343?style=for-the-badge&logo=swift&logoColor=white)](https://swift.org)

[![Visitors](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FKadiraricii%2FSentinel_Hook&count_bg=%23FF6B6B&title_bg=%23282C34&icon=github.svg&icon_color=%23E7E7E7&title=Ziyaret&edge_flat=false)](https://github.com/Kadiraricii/Sentinel_Hook)

</div>

---

## 🎯 Proje Nedir?

**Sentinel Hook**, iOS ve Android ekosistemlerindeki yüksek güvenlikli uygulamaların (Bankacılık, Kripto Cüzdanlar, Kurumsal Girişler) güvenlik katmanlarını araştıran gelişmiş bir **Dinamik Enstrümantasyon Çerçevesidir**.

Frida'nın RAM seviyesindeki gücünü kullanarak, bir uygulamanın koruma zırhını **4 ayrı katmanda** aynı anda parçalar:

```
┌─────────────────────────────────────────────────────────────────┐
│                      SENTINEL HOOK                              │
│                                                                 │
│  [01] BiometricPrompt / LocalAuthentication  →  TRUE Inject    │
│  [02] AVCaptureSession / CameraX             →  Frame Spoof    │
│  [03] CoreML / Vision / MLKit                →  AI Blind       │
│  [04] Jailbreak / SSL / Frida Detection      →  Stealth        │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Özellik Matrisi

| Modül | Platform | Teknik Yaklaşım | Durum |
|:------|:---------|:----------------|:-----:|
| **Biyometrik Bypass** | iOS · Android | `evaluatePolicy` / `BiometricPrompt.AuthCallback` hook | ✅ |
| **Kamera Frame Enjeksiyonu** | iOS · Android | `CVPixelBuffer` / `Image.Plane` bellekte değiştirme | ✅ |
| **CoreML / Vision Bypass** | iOS | `VNFaceObservation` sahte obje enjeksiyonu | ✅ |
| **Google MLKit Bypass** | Android | `FaceDetector` return değeri kancalama | ✅ |
| **OpenCV DNN Bypass** | iOS · Android | Native `cv::dnn::Net::forward` C++ hook | ✅ |
| **Root / Jailbreak Gizleme** | iOS · Android | `NSFileManager` + `stat` / `fopen` ENOENT yanıtı | ✅ |
| **SSL Pinning Bypass** | iOS · Android | `SecTrustEvaluate` + `TrustManagerImpl` yamalama | ✅ |
| **Frida Varlığı Gizleme** | iOS · Android | `/proc/self/maps` + port tarama anomali bastırma | ✅ |
| **Integrity Check Bypass** | iOS · Android | `SecStaticCodeCheckValidity` + APK İmza sahteleme | ✅ |

---

## 📂 Proje Yapısı

```
Sentinel_Hook/
│
├── 📁 src/hooks/
│   ├── 📁 01_biometrics/       ← FaceID, TouchID, BiometricPrompt kırıcılar
│   │   ├── local_auth_bypass.js
│   │   ├── biometric_callback_hook.js
│   │   └── crypto_object_bypass.js
│   │
│   ├── 📁 02_camera/           ← Kamera sensörü manipülasyonları
│   │   ├── camera_bypass.js
│   │   ├── camerax_hook.js
│   │   └── video_replayer.js
│   │
│   ├── 📁 03_ml_vision/        ← Yapay Zeka / ML kandırma
│   │   ├── vision_bypass.js
│   │   ├── mlkit_face_bypass.js
│   │   └── face_embedding_bypass.js
│   │
│   └── 📁 04_anti_tamper/      ← Görünmezlik duvarı
│       ├── root_jailbreak_bypass.js
│       ├── ssl_pinning_bypass.js
│       ├── frida_detection_bypass.js
│       └── integrity_bypass.js
│
├── 📁 tests/DummyBank/         ← SwiftUI test laboratuvarı
├── 📁 src/recon/               ← Bellek analiz scriptleri
├── 📄 README.md
├── 📄 USAGE.md                 ← Detaylı kullanım rehberi
├── 📄 ROADMAP.md
├── 📄 CONTRIBUTING.md
├── 📄 CHANGELOG.md
├── 📄 SECURITY.md
├── 📄 DISCLAIMER.md
├── 📄 requirements.txt
└── ⚙️  install.sh              ← Otomatik kurulum
```

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum (Tek Komut)
```bash
git clone https://github.com/Kadiraricii/Sentinel_Hook.git
cd Sentinel_Hook
bash install.sh
```

### 2. Cihazı Tanı
```bash
source .venv/bin/activate
frida-ps -Uai        # Bağlı cihaz uygulamalarını listele
```

### 3. Bypass Ateşle
```bash
# Tek modül
frida -U -n DummyBank -l src/hooks/01_biometrics/local_auth_bypass.js

# Çoklu modül (ALL-IN-ONE)
frida -U -n DummyBank \
    -l src/hooks/04_anti_tamper/root_jailbreak_bypass.js \
    -l src/hooks/02_camera/camera_bypass.js \
    -l src/hooks/03_ml_vision/vision_bypass.js
```

> 📖 Detaylı test senaryoları için **[USAGE.md](./USAGE.md)** dosyasına bakın.

---

## 🗺️ Yol Haritası

| Faz | Kapsam | Durum |
|:----|:-------|:-----:|
| Phase 2 | Biometric Logic Bypass | 🟢 Tamamlandı |
| Phase 3 | Camera & Sensor Spoofing | 🟢 Tamamlandı |
| Phase 4 | AI / ML Liveness Bypass | 🟢 Tamamlandı |
| Phase 5 | Anti-Tamper & Stealth | 🟢 Tamamlandı |
| Phase 6 | CLI Otomasyon & Dashboard | 🟡 Devam Ediyor |
| Phase 7 | Kernel-Level Evasion (ARM64e) | ⚪️ Planlandı |

---

## ⚖️ Yasal Uyarı

> Bu proje yalnızca **eğitim ve siber güvenlik araştırmaları** (Red Teaming, Penetration Testing) amacıyla geliştirilmiştir. İzin verilmemiş sistemlerde kullanılması yasaktır. Detaylar için **[DISCLAIMER.md](./DISCLAIMER.md)** okuyun.

---

<div align="center">

**Sentinel Hook** ile güvenliği anlayın, daha iyisini inşa edin.

[![GitHub](https://img.shields.io/badge/github-Kadiraricii-181717?style=for-the-badge&logo=github)](https://github.com/Kadiraricii)

</div>
