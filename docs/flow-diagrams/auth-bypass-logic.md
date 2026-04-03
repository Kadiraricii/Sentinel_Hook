# 🔐 Auth Bypass Logic — Biyometrik Doğrulama Akışı

> **Phase 9.2 — Akış Diyagramları**  
> **Konu:** Normal Biyometrik Doğrulama vs. Sentinel Hook Bypass  
> **İlgili Modül:** `hooks/ios/keychain.js`, `LAContext`  
> **Önceki Referans:** `biometric-auth-flow.md` (Phase 1.3)

---

## 1. Normal Akış — Donanım Tabanlı Doğrulama

Kullanıcının herhangi bir müdahale olmaksızın Face ID / Touch ID ile uygulamaya girdiği standart akış. Her katmanın kendi sorumluluğu vardır ve zincirin herhangi bir halkası kırılırsa giriş reddedilir.

```mermaid
sequenceDiagram
    autonumber
    participant U  as 👤 Kullanıcı
    participant A  as 📱 Uygulama (App Layer)
    participant LA as 🔑 LAContext (LocalAuthentication)
    participant SE as 🔒 Secure Enclave (TEE)
    participant HW as 📷 Biyometrik Donanım

    U  ->> A  : Uygulamayı açar / "Giriş Yap" butonuna basar
    A  ->> LA : canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics)

    alt Donanım Mevcut Değil veya Kilitli
        LA -->> A  : false + LAError(.biometryNotAvailable)
        A  -->> U  : "Face ID kullanılamıyor" uyarısı göster
    else Donanım Hazır
        LA -->> A  : true
        A  ->> LA : evaluatePolicy(reason: "Kimliğinizi doğrulayın", reply: replyBlock)
        LA ->> HW : Tarama isteği başlat (IR projektör / TrueDepth / kapasitif sensör)
        HW -->> U : Biyometrik veri topla (yüz tarama / parmak izi)
        U  -->> HW: Yüz göster / parmağını bas

        alt Eşleşme Başarısız (3 deneme)
            HW -->> SE : Negatif sinyal
            SE -->> LA : Doğrulama Hatası
            LA -->> A  : replyBlock(false, LAError(.authenticationFailed))
            A  -->> U  : "Face ID eşleşmedi" — PIN fallback teklif et
        else Eşleşme Başarılı
            HW -->> SE : Pozitif sinyal
            SE -->> LA : Kriptografik onay (Enclave-bound key imzalar)
            LA -->> A  : replyBlock(true, nil)
            A  ->> A   : Keychain'den token çöz, login akışını başlat
            A  -->> U  : Ana ekran açılır ✅
        end
    end
```

---

## 2. Sentinel Hook Bypass — Tam Yol Haritası

Frida enjeksiyonu sonrası Sentinel'in her iki kontrol noktasını (`canEvaluatePolicy` + `replyBlock`) nasıl ele geçirdiği. Donanım **hiç tetiklenmez**.

```mermaid
sequenceDiagram
    autonumber
    participant R  as 🎯 Araştırmacı (Python)
    participant F  as ⚡ Sentinel Hook (Frida/JS)
    participant A  as 📱 Uygulama (App Layer)
    participant LA as 🔑 LAContext
    participant SE as 🔒 Secure Enclave

    Note over R,F: Ön Hazırlık — Hook Enjeksiyonu
    R  ->> F  : sentinel_orchestrator.py → script.load()
    F  ->> A  : Interceptor.attach(LAContext metodları)
    F  -->> R : send({type: "ready"})

    Note over A,LA: Uygulama Normal Akışını Başlatıyor
    A  ->> LA : canEvaluatePolicy()

    Note over F,LA: ⚡ HOOK-1: Ön Kontrol Geçişi
    F  ->> F  : onLeave → retval.replace(ptr(1))
    F  -->> A : TRUE döner (Donanım YOKKEN bile!)

    A  ->> LA : evaluatePolicy(reason, replyBlock)

    Note over F,LA: ⚡ HOOK-2: replyBlock Kaçırma
    F  ->> F  : onEnter → replyBlock closure pointer'ı kaydet
    F  ->> F  : Orijinal evaluatePolicy çağrısını ENGELLE
    F  ->> A  : replyBlock(success: true, error: nil) — sahte sinyal

    Note over SE: Secure Enclave HİÇ tetiklenmedi
    Note over A: App sadece replyBlock sonucuna bakıyor

    A  ->> A  : Login akışını başlat (token çözme)
    A  -->> R : send({type: "bypass_success"})
    R  ->> R  : Log yaz, session kaydet
```

---

## 3. Karşılaştırma: Normal vs. Bypass

```mermaid
graph LR
    subgraph NORMAL["✅ Normal Akış"]
        direction TB
        N1([Kullanıcı]) --> N2[canEvaluatePolicy]
        N2 --> N3[evaluatePolicy]
        N3 --> N4[Secure Enclave Tarama]
        N4 --> N5{Eşleşti?}
        N5 -->|Evet| N6[replyBlock true]
        N5 -->|Hayır| N7[replyBlock false]
        N6 --> N8([Giriş ✅])
        N7 --> N9([Hata ❌])
    end

    subgraph BYPASS["⚡ Sentinel Bypass"]
        direction TB
        B1([Araştırmacı]) --> B2[canEvaluatePolicy]
        B2 -->|HOOK-1| B3{{Sentinel: TRUE}}
        B3 --> B4[evaluatePolicy]
        B4 -->|HOOK-2| B5{{Sentinel: replyBlock true}}
        B5 --> B6([Giriş ✅ — Donanım Atlandı])

        style B3 fill:#ff6b6b,color:#fff
        style B5 fill:#ff6b6b,color:#fff
    end
```

---

## 4. Neden CryptoObject Bypass'ı Engeller?

Eğer uygulama `replyBlock` yerine **Enclave-Bound Key** kullanıyorsa bypass başarısız olur:

```mermaid
sequenceDiagram
    participant F  as ⚡ Sentinel Hook
    participant A  as 📱 Uygulama
    participant SE as 🔒 Secure Enclave

    A  ->> SE : SecAccessControlCreateWithFlags(.biometryCurrentSet)
    Note over A,SE: Anahtar, biyometrik donanıma kriptografik bağlı

    A  ->> F  : evaluatePolicy çağrısı
    F  -->> A : replyBlock(true, nil) — SAHTE BAŞARI

    A  ->> SE : SecKeyCreateSignature() — token imzalama isteği
    SE -->> A : errSecAuthFailed ❌
    Note over SE: Gerçek donanım onayı olmadan imza üretemez

    A  -->> F  : Login akışı başlamaz — BYPASS BAŞARISIZ
```

> **Savunma notu:** `kSecAccessControlBiometryCurrentSet` + `CryptoObject` kombinasyonu, `replyBlock` manipülasyonunu işlevsiz kılar. Bkz. `HOOK_REFERENCE.md § Keychain — Biyometrik Bağlı Anahtar`.

---

*Bkz: [`camera-injection-pipeline.md`](camera-injection-pipeline.md) · [`hook-loading-sequence.md`](hook-loading-sequence.md) · [`HOOK_REFERENCE.md`](../HOOK_REFERENCE.md)*
