/**
 * Sentinel Hook - Biometric Capability Spoofing (Phase 2.4)
 * Cihazın Biyometrik kapasitesini sistem servisine manipüle etme.
 */

Java.perform(function () {
    console.log("[*] Sentinel Hook: Biometric Capability Spoofing Yükleniyor...");

    // Hedef cihaz fiziksel bir sensöre sahip olmasa dahi, sisteme "Bende sensör var" yalanı söylenir.
    try {
        var biometricManagerClass = Java.use("androidx.biometric.BiometricManager");
        
        biometricManagerClass.canAuthenticate.overload().implementation = function () {
            console.log("[💥] SENTINEL SPOOF: canAuthenticate() -> Her zaman BIOMETRIC_SUCCESS dönüyoruz.");
            // 0 = BIOMETRIC_SUCCESS
            return 0; 
        };

        biometricManagerClass.canAuthenticate.overload('int').implementation = function (authenticators) {
            console.log("[💥] SENTINEL SPOOF: canAuthenticate(int) -> Her zaman BIOMETRIC_SUCCESS dönüyoruz.");
            return 0;
        };

    } catch (e) {
        console.log("[-] BiometricManager spoof edilemedi (Sürüm uyumsuzluğu olabilir).");
    }

    try {
        var packageManager = Java.use("android.app.ApplicationPackageManager");
        packageManager.hasSystemFeature.overload('java.lang.String').implementation = function (featureName) {
            if (featureName === "android.hardware.fingerprint" || featureName === "android.hardware.biometrics.face") {
                console.log("[💥] SENTINEL SPOOF: hasSystemFeature(" + featureName + ") -> TRUE dönüyoruz.");
                return true;
            }
            return this.hasSystemFeature(featureName);
        };
    } catch (e) {
        console.log("[-] PackageManager spoof edilemedi.");
    }
});
