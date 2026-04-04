# 📦 Sentinel Hook - Değişiklik Günlüğü (CHANGELOG)

Bu dosya, projenin tüm önemli değişikliklerini kronolojik sırayla belgeler.
Format: [Semantic Versioning](https://semver.org/) — `[Versiyon] - YYYY-AA-GG`

---

## [1.0.0] - 2026-04-04

### 🎉 İlk Stabil Sürüm

**Eklendi:**
- **Phase 2 — Biometric Logic Bypass:**
  - `01_biometrics/local_auth_bypass.js` → iOS `LocalAuthentication` framework hook'u
  - `01_biometrics/biometric_callback_hook.js` → Android `BiometricPrompt` callback kırıcı
  - `01_biometrics/crypto_object_bypass.js` → Android `CryptoObject` donanım kilidi bypass

- **Phase 3 — Camera & Sensor Spoofing:**
  - `02_camera/camera_bypass.js` → iOS `AVCaptureSession` frame enjeksiyonu (hacker.jpg)
  - `02_camera/camerax_hook.js` → Android `CameraX/Camera2` ImageReader bypass
  - `02_camera/video_replayer.js` → 60 FPS sahte video stream enjeksiyonu
  
- **Phase 4 — AI / ML Bypass:**
  - `03_ml_vision/vision_bypass.js` → Apple CoreML `VNFaceObservation` sahte obje enjeksiyonu
  - `03_ml_vision/mlkit_face_bypass.js` → Google MLKit yüz tespiti bypass
  - `03_ml_vision/face_embedding_bypass.js` → FaceNet embedding distance manipülasyonu
  - `opencv_bypass.js` → Native C++ `cv::dnn::Net::forward` AI skorlama bypass

- **Phase 5 — Anti-Tamper / Stealth:**
  - `04_anti_tamper/root_jailbreak_bypass.js` → `NSFileManager` ObjC hook ile Cydia/Sileo gizleme
  - `04_anti_tamper/ssl_pinning_bypass.js` → iOS `SecTrustEvaluate` + Android `TrustManagerImpl` bypass
  - `04_anti_tamper/frida_detection_bypass.js` → `/proc/self/maps` ve ptrace anti-debug bypass
  - `04_anti_tamper/integrity_bypass.js` → APK imzası + iOS `SecStaticCodeCheckValidity` bypass

- **DummyBank Test Laboratuvarı:**
  - SwiftUI tabanlı simülatör uygulaması eklendi
  - Jailbreak tespiti simülasyonu (Safari → Cydia proxy testi) eklendi
  - `CameraManager.swift` → Frida hook edilebilir `simulateFrameTrigger` metodu

- **Proje Dökümanları:**
  - `README.md`, `ROADMAP.md`, `USAGE.md`, `DISCLAIMER.md`, `CONTRIBUTING.md` eklendi
  - `requirements.txt` ve `install.sh` otomatik kurulum scripti eklendi

**Düzeltildi:**
- `camera_bypass.js` → `ptr()` yerine `ObjC.classes` kullanımı ile `TypeError` giderildi
- `root_jailbreak_bypass.js` → iOS Simülatöründe `fopen/stat` nullptr hatası, `NSFileManager` hook ile çözüldü
- `BiometricAuthManager.swift` → Eksik `import Combine` eklendi

---

## [0.3.0] - 2026-04-03

### Phase 4 (ML Bypass) tamamlandı
- Vision Framework ve Google MLKit hook'ları yazıldı
- OpenCV native katman manipülasyonu eklendi

## [0.2.0] - 2026-04-03

### Phase 3 (Camera Spoofing) tamamlandı
- DummyBank uygulamasına AVCaptureSession entegre edildi
- Frida ile statik frame enjeksiyonu başarıyla test edildi

## [0.1.0] - 2026-04-03

### Phase 2 (Biometric Logic Bypass) tamamlandı
- iOS LocalAuthentication ve Android BiometricPrompt kancaları yazıldı
- Proje iskelet yapısı ve Frida altyapısı kuruldu
