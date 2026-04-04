/**
 * Sentinel Hook - Biometric Callback Hook (Phase 2.1 & 2.2)
 * Android BiometricPrompt ve FingerprintManager Logic Bypass.
 */

Java.perform(function () {
    console.log("[*] Sentinel Hook: BiometricPrompt & FingerprintManager Callback Bypass Yükleniyor...");

    // 1. AndroidX BiometricPrompt.AuthenticationCallback Bypass
    try {
        var biometricPromptCallback = Java.use('androidx.biometric.BiometricPrompt$AuthenticationCallback');
        
        biometricPromptCallback.onAuthenticationError.implementation = function(errorCode, errString) {
            console.log("[💥] SENTINEL İPTAL ETTİ: Biometric Error fırlatıldı (" + errString + "). Bunu BAŞARI'ya çeviriyoruz!");
            // Aslında hata alındı (örn: iptal tuşuna basıldı) ama biz bunu success'e çeviriyoruz.
            // BiometricPrompt.AuthenticationResult class'ını mock etmemiz gerekir, basit bypass için kendi success'imizi tetikleriz:
            this.onAuthenticationSucceeded(null); // veya sahte result
        };

        biometricPromptCallback.onAuthenticationFailed.implementation = function() {
            console.log("[💥] SENTINEL İPTAL ETTİ: Biometric Failed! Yüz/Parmak Tanınmadı. BAŞARI'ya çeviriyoruz!");
            this.onAuthenticationSucceeded(null);
        };
        
        console.log("[+] AndroidX BiometricPrompt hooklandı.");
    } catch (e) {
        console.log("[-] AndroidX BiometricPrompt bulunamadı (Eski cihaz/uygulama olabilir).");
    }

    // 2. Fallback: Eski FingerprintManager API Bypass
    try {
        var fingerprintManagerCallback = Java.use('android.hardware.fingerprint.FingerprintManager$AuthenticationCallback');

        fingerprintManagerCallback.onAuthenticationFailed.implementation = function() {
            console.log("[💥] SENTINEL İPTAL ETTİ: Fingerprint Failed! BAŞARI'ya çeviriyoruz!");
            this.onAuthenticationSucceeded(null);
        };

        console.log("[+] Legacy FingerprintManager hooklandı.");
    } catch (e) {
        console.log("[-] Legacy FingerprintManager bulunamadı.");
    }

});
