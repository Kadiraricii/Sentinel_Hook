# 🔄 Biyometrik Doğrulama Akış Diyagramı (iOS ve Android Olguları)
> Phase 1.3 Çıktısı

Hedef bir bankacılık veya kilit uygulamasının biyometrik koruma altyapısını ve bizim Sentinel Hook ile bu mekanizmaya hangi noktalardan saldırdığımızı gösteren akış haritasıdır.

## 1. Uygulama İçi (Standart) Akış Şeması
Standart bir mobil uygulamanın cihazdaki biyometrik sensör ile nasıl konuştuğunu gösteren Mermaid diyagramı:

```mermaid
sequenceDiagram
    participant User as Kullanıcı
    participant App as Mobil Uygulama
    participant AuthAPI as LocalAuthentication / BiometricPrompt
    participant SecureEnclave as Secure Enclave (TEE)
    
    User->>App: "Giriş Yap" butonuna basar
    App->>AuthAPI: canEvaluatePolicy()
    
    alt Donanım Yok veya Aktif Değil
        AuthAPI-->>App: FALSE (Hata Fırlatır)
        App-->>User: "Face ID Kullanılamıyor" Uyarısı
    else Donanım Engeli Yok
        AuthAPI-->>App: TRUE
        App->>AuthAPI: evaluatePolicy(reason, replyBlock)
        AuthAPI->>SecureEnclave: Yüz / Parmak İzi Tarama İsteği Başlat
        SecureEnclave-->>User: IR Sensörü Kamera Görüntüsü alır
        User->>SecureEnclave: Biyometrik veri sağlar
        
        alt Eşleşme Yok
            SecureEnclave-->>AuthAPI: Fail (Error)
            AuthAPI-->>App: replyBlock(false, error)
        else Eşleşme Var
            SecureEnclave-->>AuthAPI: Success
            AuthAPI-->>App: replyBlock(true, nil)
            App->>App: Local Token Onaylanır, Login Fonksiyonu Tetiklenir
        end
    end
```

## 2. Sentinel Hook Bypass Akış Şeması
Sentinel Hook olarak bizim sisteme dışarıdan (Frida ile) dahil olup hem Ön-kontrolü (`canEvaluatePolicy`) hem de asıl blok fonksiyonunu (`evaluatePolicy`) nasıl kısa devre kıldığımızın algoritmasıdır:

```mermaid
sequenceDiagram
    participant User as Hacker
    participant App as Mobil Uygulama
    participant Frida as Sentinel Hook (Interceptor)
    participant AuthAPI as LocalAuthentication
    
    User->>App: "Giriş Yap" butonuna basar
    App->>AuthAPI: canEvaluatePolicy()
    
    Note over Frida,AuthAPI: [HOOK-1] Sentinel Araya Girip Ön Kontrolü Ezer
    Frida-->>App: return TRUE (Cihazda sensör olmasa bile)
    
    App->>AuthAPI: evaluatePolicy(reason, replyBlock)
    
    Note over Frida,AuthAPI: [HOOK-2] Sentinel, replyBlock parametresini RAM'de Tutar
    Frida->>Frida: Sensörden yanıt beklemeyi iptal eder!
    Frida-->>App: replyBlock(true, null) (Sahte Başarı Sinyali)
    
    App->>App: Local Token Onaylanır, ŞİFRESİZ GİRİŞ SAĞLANIR!
```

## 3. Güvenlik Notları (Mitigation)
- `replyBlock` doğrudan boolean döndürdüğü için Frida ile %100 manipüle edilebilmektedir. 
- Eğer geliştirici yalnızca `replyBlock == true` kısmına bakmak yerine, `SecAccessControlCreateWithFlags` ve `CryptoObject` kullanarak uygulamanın private key'ini bu biyometrik sensör işlemine bağlasaydı, biz `true` döndürsek bile kriptografik imza üretilmeyeceği için Bypass başarısız olacaktı. 
