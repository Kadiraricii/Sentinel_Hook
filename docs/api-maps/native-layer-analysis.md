# ⚙️ Native (C/C++) Katmanı Analiz Haritası
> Phase 1.5 Çıktısı

Özellikle Android (.so) ve iOS (dylib) uygulamalarında, geliştiriciler kritik şifreleme/imza operasyonlarını Java/Swift katmanından gizlemek için kodları C/C++ Native katmanında yazarlar. Bu belge Native taraftaki sınır kapılarını tanımlar.

## iOS Ortamında Native Analizi (Objective-C ve C)
iOS uygulamaları doğrudan Apple makine diline derlendiğinden, IPA/Mach-O dosyası Ghidra/Hopper ile açılıp statik analize tabi tutulabilir. 
1. **Hedef Fonksiyon Sembolleri:**
   - `_SecKeyCreateSignature` veya `_SecItemCopyMatching` (Keychain Data Access).
   - `_CC_SHA256` (Crypto C kütüphanesi - Biyometri onayı sonrası hash manipülasyonu için hooklanır).

2. **Jailbreak (Anti-Tamper) Korumaları:**
   - Apple uygulamaları sıklıkla `stat("/Applications/Cydia.app")` yahut `fork()` gibi C kodları ile cihazın jailbroken olup olmadığını test ederler. Bunu kırmak için (Phase 5) Frida'nın `Interceptor.attach(Module.findExportByName(null, "stat"), ...)` özelliği ile Native bypass uygulanmalıdır.

## Android Ortamında Native Analizi (.so Dosyaları)
1. **JNI (Java Native Interface):**
   - Fonksiyonların adları genellikle `Java_com_example_app_NativeClass_methodName` şeklinde export edilir.
   - Sentinel Payload, JNI köprü metodunu (`RegisterNatives`) hooklayarak gerçek .so kodu çalışmadan önce kendi C mantığını araya sokabilir.
   - Biyometrik onay sonucunda sunucuya gönderilen Crypto Hash'leri bu native katmanlarda üretildiği için `dlopen` veya `dlsym` metotlarının izlenmesi gereklidir.

**Not:** Sentinel Hook projesinin biyometrik ve kamera odaklı (Phase 2 ve 3) hedeflerinden dolayı önceliğimiz Native Katman (Phase 1.5) değil, doğrudan Object/Delegate Override yöntemleridir. Native Bypass genelde **Phase 5 (Jailbreak Detection)** için kullanılacaktır.
