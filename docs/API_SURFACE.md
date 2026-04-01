# 📡 Sentinel Hook — Hedef API Yüzey Haritası (iOS)

> **Kapsam:** iOS 14–18  
> **Referans Kaynaklar:** Apple Developer Docs, Mach-O analizi, Phase 1.3–1.5 Çıktıları  
> **Son Güncelleme:** Phase 7.3

---

## 1. `LocalAuthentication` Framework

Biyometrik doğrulamanın (Face ID, Touch ID, Optic ID) kapı bekçisi. Sentinel'in birincil hedefi.

| API / Sınıf | Method / Fonksiyon | Hook Tipi | Sentinel Etkisi |
|:-----------|:-------------------|:----------|:----------------|
| `LAContext` | `canEvaluatePolicy(_:error:)` | ObjC method | Donanım yokken `true` döndürülür |
| `LAContext` | `evaluatePolicy(_:localizedReason:reply:)` | ObjC method | `replyBlock(true, nil)` inject edilir |
| `LAContext` | `evaluateAccessControl(_:operation:localizedReason:reply:)` | ObjC method | CryptoObject bağlı bypass |
| `LAContext` | `biometryType` (property) | ObjC getter | `.faceID` veya `.touchID` döndürülür |
| `LAContext` | `interactionNotAllowed` (property) | ObjC getter | `false` döndürülür |
| `LAError` | `.authenticationFailed`, `.biometryNotAvailable` | — | `replyBlock` içindeki error `nil` yapılır |

### Kritik Bypass Noktası
```
evaluatePolicy(reply: { (success: Bool, error: Error?) in
    if success { /* GİRİŞ */ }
})
```
`reply` closure'ı Frida ile doğrudan `success = true, error = nil` parametreleriyle çağrılır.

---

## 2. `AVFoundation` Framework

Kamera akışı ve medya yakalama katmanı. Frame enjeksiyonu için birincil hedef.

| API / Sınıf | Method / Fonksiyon | Hook Tipi | Sentinel Etkisi |
|:-----------|:-------------------|:----------|:----------------|
| `AVCaptureSession` | `-startRunning` | ObjC method | Gerçek stream kontrolünü ele geçirir |
| `AVCaptureSession` | `-stopRunning` | ObjC method | Enjeksiyon sonrası temiz kapanış |
| `AVCaptureVideoDataOutput` | `-setSampleBufferDelegate:queue:` | ObjC method | Delegate pointer yakalanır |
| `AVCaptureVideoDataOutputSampleBufferDelegate` | `-captureOutput:didOutputSampleBuffer:fromConnection:` | ObjC delegate | **Ana frame enjeksiyon noktası** |
| `AVCaptureDevice` | `+defaultDeviceWithMediaType:` | ObjC class method | Kamera seçimini yönlendirir |
| `AVCaptureDeviceInput` | `+deviceInputWithDevice:error:` | ObjC class method | Girdi kaynağı değiştirilebilir |

---

## 3. `CoreMedia` Framework

Ham medya buffer yönetimi. Frame oluşturma ve manipülasyon için zorunlu.

| API / Fonksiyon | Tip | Sentinel Kullanımı |
|:---------------|:----|:-------------------|
| `CMSampleBufferGetImageBuffer` | C func | `CVPixelBufferRef` alımı |
| `CMSampleBufferCreateForImageBuffer` | C func | Sahte buffer üretimi |
| `CMSampleBufferGetPresentationTimeStamp` | C func | Zaman damgası tutarlılığı için |
| `CMFormatDescriptionGetMediaType` | C func | Buffer format kontrolü |
| `CMVideoFormatDescriptionCreateForImageBuffer` | C func | Sahte format tanımlayıcı |

---

## 4. `CoreVideo` Framework

Piksel buffer yönetimi. JPEG → CVPixelBuffer dönüşümü için kullanılır.

| API / Fonksiyon | Tip | Sentinel Kullanımı |
|:---------------|:----|:-------------------|
| `CVPixelBufferCreate` | C func | Sahte buffer alan ayırma |
| `CVPixelBufferLockBaseAddress` | C func | Ham bellek erişimi öncesi kilit |
| `CVPixelBufferUnlockBaseAddress` | C func | Kilit açma |
| `CVPixelBufferGetBaseAddress` | C func | Piksel verisi yazma pointer'ı |
| `CVPixelBufferGetWidth` / `GetHeight` | C func | Boyut doğrulama |
| `CVPixelBufferGetBytesPerRow` | C func | Satır boyutu hizalama |

---

## 5. `Security` Framework

Keychain ve kriptografik anahtar yönetimi. Token & credential çalma / inceleme için hedef.

| API / Fonksiyon | Tip | Sentinel Kullanımı |
|:---------------|:----|:-------------------|
| `SecItemCopyMatching` | C func | Keychain token okuma — ana hedef |
| `SecItemAdd` | C func | Yeni item izleme |
| `SecItemUpdate` | C func | Mevcut item değiştirme |
| `SecItemDelete` | C func | Item silme izleme |
| `SecKeyCreateSignature` | C func | Private key imza operasyonu |
| `SecKeyVerifySignature` | C func | İmza doğrulama bypass |
| `SecAccessControlCreateWithFlags` | C func | Biyometri-bound key politikası |
| `SecTrustEvaluate` / `SecTrustEvaluateWithError` | C func | SSL Pinning bypass |
| `_CC_SHA256` / `_CC_SHA512` | C func (libcommonCrypto) | Hash manipülasyonu |

---

## 6. `Vision` Framework

ML tabanlı yüz ve nesne tespiti. Liveness kontrolü bypass için hedef.

| API / Sınıf | Method | Sentinel Kullanımı |
|:-----------|:-------|:-------------------|
| `VNDetectFaceRectanglesRequest` | `-setCompletionHandler:` | Sahte yüz koordinatları inject edilir |
| `VNDetectFaceLandmarksRequest` | `-setCompletionHandler:` | Landmark sonuçları override edilir |
| `VNFaceObservation` | `boundingBox`, `landmarks` | Sahte gözlem objesi döndürülür |
| `VNImageRequestHandler` | `-performRequests:error:` | Sahte buffer ile çağrılır |
| `VNRequest` | `-results` (property) | Sonuç listesi override edilir |

---

## 7. Native / `libSystem` Katmanı (Cloak Hedefleri)

Jailbreak ve anti-tamper tespitini kapatan düşük seviyeli syscall'lar.

| Fonksiyon | Kütüphane | Tespit Yöntemi |
|:----------|:----------|:---------------|
| `stat64` | `libSystem.B.dylib` | `/Applications/Cydia.app` path kontrolü |
| `access` | `libSystem.B.dylib` | `/usr/bin/ssh`, `/bin/sh` varlık kontrolü |
| `fork` | `libSystem.B.dylib` | Sandbox anomali tespiti |
| `posix_spawn` | `libSystem.B.dylib` | Spawn davranışı analizi |
| `getenv` | `libSystem.B.dylib` | `DYLD_INSERT_LIBRARIES` kontrolü |
| `dlopen` | `libdyld.dylib` | Yüklü kütüphane taraması |
| `ptrace` | `libSystem.B.dylib` | Anti-debug (`PT_DENY_ATTACH`) |
| `sysctl` | `libSystem.B.dylib` | Debugger varlık kontrolü (`P_TRACED`) |

---

## 8. API Yüzey Özeti

| Framework | Hedef Sayısı | Öncelik | Mevcut Durum |
|:----------|:------------:|:-------:|:------------:|
| LocalAuthentication | 5 | 🔴 Kritik | ✅ Tamamlandı |
| AVFoundation | 6 | 🔴 Kritik | ✅ Tamamlandı |
| CoreMedia | 5 | 🟠 Yüksek | ✅ Tamamlandı |
| CoreVideo | 6 | 🟠 Yüksek | ✅ Tamamlandı |
| Security | 9 | 🔴 Kritik | ✅ Tamamlandı |
| Vision | 5 | 🟡 Orta | ✅ Tamamlandı |
| libSystem (Cloak) | 8 | 🔴 Kritik | ✅ Tamamlandı |
| **TOPLAM** | **44** | — | — |

---

*Bkz: [`HOOK_REFERENCE.md`](HOOK_REFERENCE.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)*
