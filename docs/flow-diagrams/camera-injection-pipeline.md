# 📷 Camera Injection Pipeline — Kamera Frame Manipülasyonu

> **Phase 9.2 — Akış Diyagramları**  
> **Konu:** AVFoundation Normal Frame Akışı vs. Sentinel Frame Enjeksiyonu  
> **İlgili Modül:** `hooks/ios/camera.js`  
> **Referans:** `api-maps/camera-surface-map.md` (Phase 1.4)

---

## 1. Normal Kamera Pipeline — Gerçek Frame Akışı

Bir liveness-check yapan uygulamanın sensörden ML katmanına kadar frame'i nasıl işlediği:

```mermaid
graph TD
    HW["📷 Fiziksel Kamera Donanımı\n(TrueDepth / RGB Sensörü)"]

    subgraph AVF["AVFoundation Katmanı"]
        ACS["AVCaptureSession\n-startRunning"]
        ACI["AVCaptureDeviceInput\n(fiziksel lens bağlantısı)"]
        ACO["AVCaptureVideoDataOutput\n-setSampleBufferDelegate:queue:"]
    end

    subgraph CM["CoreMedia / CoreVideo Katmanı"]
        CSB["CMSampleBuffer\n(ham frame verisi)"]
        CVP["CVPixelBuffer\n(piksel dizisi — RGBA / YUV)"]
    end

    subgraph DEL["Delegate Callback"]
        DID["captureOutput:\ndidOutputSampleBuffer:\nfromConnection:\n⬅ Her kare buraya düşer"]
    end

    subgraph ML["ML / Vision Katmanı"]
        VNR["VNDetectFaceRectanglesRequest\n(yüz koordinatları)"]
        VNL["VNDetectFaceLandmarksRequest\n(göz, burun, çene noktaları)"]
        LIV["Liveness Check\n(göz kırpma / baş hareketi)"]
    end

    APP["📱 Uygulama\nKimlik Doğrulama Kararı"]

    HW --> ACS
    ACS --> ACI --> ACO
    ACO --> CSB
    CSB --> CVP
    CVP --> DID
    DID --> VNR --> VNL --> LIV --> APP

    style HW fill:#4ecdc4,color:#000
    style APP fill:#45b7d1,color:#000
    style DID fill:#96ceb4,color:#000
```

---

## 2. Sentinel Frame Enjeksiyon Pipeline

`camera.js` hook'u `didOutputSampleBuffer` noktasında devreye girerek gerçek frame'i düşürür ve `Hacker.jpg` piksel verisini uygulamaya "gerçek kameradan geliyormuş gibi" sunar:

```mermaid
graph TD
    HW["📷 Fiziksel Kamera Donanımı"]
    PY["🐍 Python Orchestrator\n(payload yolu RPC ile gönderilir)"]
    JPG["🖼️ Hacker.jpg\n(.local/test-faces/face.jpg)"]

    subgraph AVF["AVFoundation Katmanı — Değişmedi"]
        ACS["AVCaptureSession -startRunning"]
        ACO["AVCaptureVideoDataOutput\n-setSampleBufferDelegate:queue:"]
    end

    subgraph HOOK["⚡ Sentinel Hook — camera.js"]
        H1["HOOK-1: setSampleBufferDelegate\nDelegate pointer yakalandı\nQueue referansı saklandı"]
        H2["HOOK-2: didOutputSampleBuffer\nGerçek CMSampleBuffer DURDURULDU ❌"]
        H3["Payload Yükle:\nUIImage → CIImage → CVPixelBuffer"]
        H4["Sahte CMSampleBuffer Oluştur\n(orijinal timestamp korunur)"]
        H5["Sahte buffer, orijinal\nDelegate'e iletilir ✅"]
    end

    subgraph CM["CoreMedia / CoreVideo — Sahte Veri"]
        FVP["Fake CVPixelBuffer\n(Hacker.jpg piksel verisi)"]
        FSB["Fake CMSampleBuffer\n(gerçek timestamp + sahte piksel)"]
    end

    subgraph ML["ML / Vision Katmanı — Aldatıldı"]
        VNR["VNDetectFaceRectanglesRequest\nSahte yüz koordinatlarını alır"]
        LIV["Liveness Check\nSahte frame'de 'canlı yüz' bulur"]
    end

    APP["📱 Uygulama\n✅ Kimlik Doğrulandı"]

    HW -->|Gerçek frame| ACS --> ACO
    ACO --> H1 --> H2
    PY -->|rpc: inject_frame(path)| JPG --> H3 --> H4 --> FVP --> FSB --> H5
    H2 -.->|DROP| X["❌ Gerçek frame çöpe gider"]
    H5 --> VNR --> LIV --> APP

    style H2 fill:#ff6b6b,color:#fff
    style H3 fill:#ffa07a,color:#000
    style H4 fill:#ffa07a,color:#000
    style H5 fill:#98d4a3,color:#000
    style X fill:#ccc,color:#666,stroke-dasharray: 5 5
    style APP fill:#45b7d1,color:#000
```

---

## 3. CVPixelBuffer Dönüşüm Detayı

JPEG dosyasının `CMSampleBuffer`'a dönüştürülme adımları:

```mermaid
graph LR
    subgraph INPUT["Giriş"]
        J["Hacker.jpg\n(disk üzerinde)"]
    end

    subgraph CONV["Dönüşüm Zinciri (JS/ObjC)"]
        direction TB
        C1["NSData\n(dosya byte'ları)"]
        C2["UIImage\n(yüksek seviyeli görüntü objesi)"]
        C3["CIImage\n(CoreImage — filtre katmanı)"]
        C4["CVPixelBuffer\n(format: kCVPixelFormatType_420YpCbCr8\nBiPlanarFullRange)"]
        C5["CMVideoFormatDescription\n(format tanımlayıcı)"]
        C6["CMSampleBuffer\n(timestamp + format + piksel)"]
    end

    subgraph OUTPUT["Çıkış"]
        O["didOutputSampleBuffer\nDelegate'e iletilir"]
    end

    J --> C1 --> C2 --> C3 --> C4
    C4 --> C5
    C4 --> C6
    C5 --> C6
    C6 --> O

    style C4 fill:#ff6b6b,color:#fff
    style C6 fill:#ffa07a,color:#000
```

> **Kritik:** `CVPixelBuffer` formatı hedef uygulamanın beklentisiyle eşleşmezse `CVReturn -6680` hatası alınır.  
> Çözüm: Orijinal buffer'dan `CVPixelBufferGetPixelFormatType()` ile format alınıp aynısı kullanılır.  
> Bkz. `TROUBLESHOOTING.md § CVReturn error: -6680`.

---

## 4. iOS Sürümüne Göre Başarı Oranı

```mermaid
graph LR
    subgraph COMPAT["Uyumluluk (camera-surface-map.md · Phase 7.3)"]
        I14["iOS 14.x\n✅ %100"]
        I15["iOS 15.x\n✅ %98"]
        I16["iOS 16.x\n✅ %95"]
        I17["iOS 17.x\n🟡 %90"]
        I18["iOS 18 Beta\n🔴 %60\nCVPixelBuffer\nformat değişti"]
    end

    I14 --> I15 --> I16 --> I17 --> I18

    style I14 fill:#98d4a3,color:#000
    style I15 fill:#98d4a3,color:#000
    style I16 fill:#b8e0b8,color:#000
    style I17 fill:#ffd700,color:#000
    style I18 fill:#ff6b6b,color:#fff
```

---

*Bkz: [`auth-bypass-logic.md`](auth-bypass-logic.md) · [`hook-loading-sequence.md`](hook-loading-sequence.md) · [`HOOK_REFERENCE.md`](../HOOK_REFERENCE.md)*
