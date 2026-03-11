# 📷 Kamera ve Yüz Enjeksiyonu (Surface) API Haritası
> Phase 1.4 Çıktısı

Bir sonraki aşama olan (Phase 3) "Kamera Frame Çalma ve Statik Görüntü Enjeksiyonu" hedeflerimiz için iOS ve Android platformlarındaki Native Kamera frameworklerinin yüzey haritasıdır.

## iOS Kamera Yüzeyi (AVFoundation Katmanı)

iOS cihazlarda gelişmiş uygulamalar direkt `UIImagePickerController` kullanmaz, Liveness (canlılık ve derinlik) tespiti yapabilmek için canlı akış alabileceği **AVFoundation** kütüphanesini kullanır.

1. **`AVCaptureSession`**: 
   - Kameraları başlatan ve stream'i (akışı) yöneten ana objedir.
   - Sentinel Hedefi: `- startRunning` fonksiyonu kapatılıp, yapay bir stream başlatılabilir.

2. **`AVCaptureVideoDataOutputSampleBufferDelegate` (KRİTİK HEDEF!)**:
   - `captureOutput:didOutputSampleBuffer:fromConnection:`
   - Gerçek hayatta her milisaniye kameradan alınan fotoğraf (Frame), bir `CMSampleBufferRef` formatında bu fonksiyona dökülür. Yapay zeka ve liveness kontrolleri bu fonksiyonun içinde çalışır.
   - **Saldırı Vektörü:** Bu fonksiyon hooking ile durdurulur ve oradayken kullanıcının belirlediği statik JPEG yüz fotoğrafı `CVPixelBuffer`'a çevrilip bu metoda sanki "gerçek kameradan geliyormuş gibi" iletilir.

## Android Kamera Yüzeyi (Camera2 & CameraX Katmanı)

Android'de donanım parçalanması çok yüksek olduğu için geliştiriciler genellikle Camera2 veya Google CameraX kullanır.

1. **Camera2 API (`android.hardware.camera2`)**:
   - `CameraCaptureSession.CaptureCallback` 
   - `ImageReader.OnImageAvailableListener` -> Buraya düşen `Image` objesi byte dizisine çevrilip hacker tarafından değiştirilebilir.

2. **Yapay Zeka (ML Kit / CoreML) Sınıfları**:
   - Bir uygulama kamerayı okurken aynı zamanda göz kırpması veya kafasını çevirmesi istiyorsa (Liveness), `FaceDetector.process()` metodunda manipülasyon yapmamız gerekir. Olası kütüphaneler:
   - *Android:* `com.google.mlkit.vision.face.FaceDetector`
   - *iOS:* `VNDetectFaceRectanglesRequest` (Vision Framework) 

Bu haritaya göre Phase 3 adımındaki "AVCaptureSession Bypass" operasyonu, iOS `CoreMedia` ve `CVPixelBuffer` yapılarını RAM üzerinde zorla şekillendirerek sağlanacaktır.
