/**
 * Sentinel Hook - CryptoObject ve Cipher Bypass (Phase 2.3)
 * Şifreli Biyometrik Doğrulamayı sağlayan KeyStore ve Cipher araçlarının sahteleştirilmesi.
 */

Java.perform(function () {
    console.log("[*] Sentinel Hook: CryptoObject Bypass Yükleniyor...");

    // Özellikle bankacılık uygulamalarında, onAuthenticationSucceeded methodu bir CryptoObject
    // bekler. Bu nesnenin null dönmesi crash'e yol açabilir. Biz de sistemi "Şifreleme yapılıyor" sanması
    // için Cipher sınıfını manipüle ediyoruz.
    
    try {
        var cipherClass = Java.use('javax.crypto.Cipher');
        
        // doFinal() metotlarının tüm varyasyonlarına hook at.
        var overloads = cipherClass.doFinal.overloads;
        for (var i = 0; i < overloads.length; i++) {
            overloads[i].implementation = function () {
                console.log("[🔥] CryptoObject / Cipher.doFinal çağrıldı! Hedef Bypass Ediliyor.");
                
                // Cihaz "imzalanamadı" hatası verecek olsa bile, biz uygulamanın beklediği byte dizisini döneceğiz.
                // Eğer uygulama spesifik bir veri beklemiyorsa, byte[0] dönmek crash'i önler.
                try {
                    return this.doFinal.apply(this, arguments);
                } catch (err) {
                    console.log("    [!] Orijinal şifreleme başarısız. Null fallback uygulanıyor.");
                    var emptyByteArray = Java.array('byte', []);
                    return emptyByteArray;
                }
            };
        }
        console.log("[+] javax.crypto.Cipher hooklandı.");
    } catch (e) {
        console.log("[-] Cipher bypass edilemedi: " + e);
    }
});
