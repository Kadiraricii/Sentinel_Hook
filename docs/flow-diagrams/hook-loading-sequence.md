# ⚙️ Hook Loading Sequence — Yükleme Sırası & Bağımlılık Grafiği

> **Phase 9.2 — Akış Diyagramları**  
> **Konu:** `sentinel_loader.js` Başlatma Akışı — Neden Sıra Kritik?  
> **İlgili Modül:** `sentinel_loader.js`, `hooks/ios/cloak.js`  
> **Referans:** `ARCHITECTURE.md § Modüller Arası İletişim`

---

## 1. Yükleme Durumu Diyagramı

`sentinel_loader.js`'in başlatma anından tüm hook'ların aktifleşmesine kadar geçen durum makinesi:

```mermaid
stateDiagram-v2
    [*] --> IDLE : Python: script.load()

    IDLE --> PLATFORM_DETECT : rpc.exports.init(config) çağrıldı

    PLATFORM_DETECT --> CLOAK_LOAD : ObjC.available == true (iOS)
    PLATFORM_DETECT --> ANDROID_PATH : Java.available == true (Android)
    PLATFORM_DETECT --> ERROR_UNSUPPORTED : Platform tespit edilemedi

    state CLOAK_LOAD {
        [*] --> cloak_attaching
        cloak_attaching --> cloak_verify : stat64 + access + fork hooked
        cloak_verify --> cloak_ready : Jailbreak gizleme aktif ✅
        cloak_attaching --> cloak_failed : Module bulunamadı / hata
    }

    CLOAK_LOAD --> KEYCHAIN_LOAD : cloak_ready
    CLOAK_LOAD --> ERROR_CLOAK : cloak_failed

    state KEYCHAIN_LOAD {
        [*] --> keychain_attaching
        keychain_attaching --> keychain_verify : SecItemCopyMatching hooked
        keychain_verify --> keychain_ready : Keychain izleme aktif ✅
        keychain_attaching --> keychain_failed : Security.framework yüklenemedi
    }

    KEYCHAIN_LOAD --> CAMERA_LOAD : keychain_ready && config.cameraEnabled
    KEYCHAIN_LOAD --> ALL_READY   : keychain_ready && !config.cameraEnabled
    KEYCHAIN_LOAD --> ERROR_KEYCHAIN : keychain_failed

    state CAMERA_LOAD {
        [*] --> camera_attaching
        camera_attaching --> delegate_capture : setSampleBufferDelegate hooked
        delegate_capture --> frame_intercept  : didOutputSampleBuffer hooked
        frame_intercept  --> camera_ready     : Frame enjeksiyonu aktif ✅
        camera_attaching --> camera_failed    : AVFoundation hook hatası
    }

    CAMERA_LOAD --> ALL_READY   : camera_ready
    CAMERA_LOAD --> ERROR_CAMERA : camera_failed

    ALL_READY --> RUNNING : send({type: "ready"})
    RUNNING --> TEARDOWN : rpc.exports.teardown() veya Ctrl+C

    state TEARDOWN {
        [*] --> detach_hooks
        detach_hooks --> clear_memory
        clear_memory --> teardown_done
    }

    TEARDOWN --> [*] : teardown_done

    ERROR_UNSUPPORTED --> [*]
    ERROR_CLOAK --> [*]
    ERROR_KEYCHAIN --> [*]
    ERROR_CAMERA --> RUNNING : Safe Boot — kamera hook atlanır, devam et
```

---

## 2. Neden Sıra Kritik? — Bağımlılık Grafiği

```mermaid
graph TD
    subgraph ORDER["Yükleme Sırası — Neden Bu Sıra?"]
        direction TB

        S["🚀 sentinel_loader.js\nBaşlangıç"]

        subgraph C1["① CLOAK — Stealth Shield"]
            CL["hooks/ios/cloak.js\n\n• stat64 hook\n• access hook\n• fork hook\n• dlopen hook\n• ptrace hook"]
            CW["⚠️ Bu yüklenmeden devam edilemez!\nApp debugger tespiti yapabilir."]
        end

        subgraph C2["② KEYCHAIN — Credential Layer"]
            KL["hooks/ios/keychain.js\n\n• SecItemCopyMatching hook\n• SecKeyCreateSignature hook\n• LAContext evaluatePolicy hook"]
            KD["🔗 Bağımlılık:\nCloak aktifse app\nhook'u jailbreak\nolarak algılamaz"]
        end

        subgraph C3["③ CAMERA — Sensor Spoof"]
            CAL["hooks/ios/camera.js\n\n• AVCaptureSession hook\n• setSampleBufferDelegate hook\n• didOutputSampleBuffer hook"]
            CD["🔗 Bağımlılık:\nKeychain hook'u\nbiyometrik bypass\nyaptıktan sonra\ncamera hook anlam\nkazanır"]
        end

        DONE["✅ ALL READY\nsend({type: 'ready'})"]
    end

    S --> CL
    CL --> CW
    CW --> KL
    KL --> KD
    KD --> CAL
    CAL --> CD
    CD --> DONE

    style CW fill:#ff6b6b,color:#fff
    style KD fill:#ffd700,color:#000
    style CD fill:#ffd700,color:#000
    style DONE fill:#98d4a3,color:#000
```

---

## 3. Yanlış Sıra — Ne Olur?

```mermaid
sequenceDiagram
    autonumber
    participant L  as sentinel_loader.js
    participant CA as camera.js (Önce Yüklendi ❌)
    participant A  as Hedef Uygulama
    participant AD as Anti-Debug Sistemi

    Note over L,CA: ❌ YANLIŞ SENARYO: Cloak yüklenmeden Camera yükleniyor

    L  ->> CA : camera.js attach()
    CA ->> A  : AVCaptureSession hook inject edildi

    Note over A,AD: App arka planda anti-tamper rutini çalıştırıyor
    A  ->> AD : stat("/Applications/Cydia.app") → BAŞARILI (Cloak yok!)
    A  ->> AD : fork() anomalisi tespit edildi
    AD -->> A : JAILBREAK TESPİT EDİLDİ 🚨

    A  -->> L  : App çöküyor (SIGKILL / abort())
    Note over L: Camera hook işe yaramadı, session sonlandı

    rect rgb(255, 200, 200)
        Note over L,AD: TÜM OTURUM ÇÖKTÜ — Sıfırdan başlanması gerekiyor
    end
```

```mermaid
sequenceDiagram
    autonumber
    participant L  as sentinel_loader.js
    participant CL as cloak.js (Önce ✅)
    participant CA as camera.js (Sonra ✅)
    participant A  as Hedef Uygulama
    participant AD as Anti-Debug Sistemi

    Note over L,CL: ✅ DOĞRU SENARYO: Cloak önce, Camera sonra

    L  ->> CL : cloak.js attach()
    CL ->> A  : stat64, fork, dlopen hook'ları aktif

    Note over A,AD: App anti-tamper rutini çalıştırıyor
    A  ->> AD : stat("/Applications/Cydia.app")
    CL -->> A : -1 döner (Dosya yokmuş gibi) ✅
    A  ->> AD : fork() çağrısı
    CL -->> A : Normal döner ✅
    AD -->> A : Temiz cihaz — devam et

    L  ->> CA : camera.js attach()
    CA ->> A  : AVCaptureSession hook inject edildi ✅

    rect rgb(200, 255, 200)
        Note over L,AD: Tüm hook'lar başarıyla yüklendi
    end
```

---

## 4. Safe Boot Mekanizması

Bir modül yüklenemezse `safe_boot.js` zinciri kırılmadan devam eder:

```mermaid
graph TD
    TRY["safeAttach(target, callbacks)\ncall"]
    TRY --> RUN["Interceptor.attach() dene"]

    RUN --> OK["✅ Hook başarılı\nModül aktif"]
    RUN --> ERR["❌ Hata (exception)"]

    ERR --> LOG["send({type: 'hook_error',\ntarget: ..., error: ...})"]
    LOG --> SKIP["Bu hook atlanır\nBir sonraki modüle geç"]
    SKIP --> CONT["Oturum devam eder\n(crash yok)"]

    OK --> NEXT["Bir sonraki modül"]

    style ERR fill:#ff6b6b,color:#fff
    style SKIP fill:#ffd700,color:#000
    style CONT fill:#98d4a3,color:#000
```

> **Not:** `cloak.js` hatası tek istisnadır — Stealth Shield yüklenemezse oturum **her zaman** durdurulur. Diğer modül hataları Safe Boot ile atlanabilir.

---

## 5. Yükleme Sırası Özet Tablosu

| Sıra | Modül | Bağımlılık | Hata Davranışı |
|:----:|:------|:-----------|:---------------|
| ① | `cloak.js` | Yok — ilk her zaman bu | **FATAL** — oturum durdurulur |
| ② | `keychain.js` | Cloak aktif olmalı | Safe Boot — atlanır, devam |
| ③ | `camera.js` | Cloak + config.cameraEnabled | Safe Boot — atlanır, devam |

---

*Bkz: [`auth-bypass-logic.md`](auth-bypass-logic.md) · [`camera-injection-pipeline.md`](camera-injection-pipeline.md) · [`ARCHITECTURE.md`](../ARCHITECTURE.md)*
