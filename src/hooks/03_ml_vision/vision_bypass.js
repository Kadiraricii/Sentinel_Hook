/**
 * Sentinel Hook - Enterprise AI Vision Bypass
 * Target: CoreML / Vision Framework Liveness Detection
 * Defense: Robust Swift Object Pointer Retention
 */

if (ObjC.available) {
    console.log("[🌟] SENTINEL SUBSYSTEM: Initiating ML Vision Override");

    var VNDetectFaceRectanglesRequest = ObjC.classes.VNDetectFaceRectanglesRequest;
    var VNFaceObservation = ObjC.classes.VNFaceObservation;
    var NSArray = ObjC.classes.NSArray;
    
    if (VNDetectFaceRectanglesRequest && VNFaceObservation) {
        console.log("[+] TARGET LOCKED: Vision Engine mapped. Patching arrays...");
        
        var cachedFakeResults = null;
        var lastLogTime = 0;

        try {
            Interceptor.attach(VNDetectFaceRectanglesRequest["- results"].implementation, {
                onLeave: function(retval) {
                    try {
                        if (!cachedFakeResults) {
                            // Swift array bridging memory protection
                            var face = VNFaceObservation.alloc().init();
                            var array = NSArray.arrayWithObject_(face);
                            
                            // Prevent Frida GC from annihilating Swift objects
                            cachedFakeResults = array.retain(); 
                            face.retain(); 
                            
                            console.log("[+] MEMORY PATCH: Allocated persistent synthetic observation.");
                        }

                        // Override output
                        retval.replace(cachedFakeResults);

                        var now = Date.now();
                        if (now - lastLogTime > 4000) {
                            console.log("[💥] SENTINEL INTEL: ML Vision Engine successfully spoofed. (Trust established)");
                            lastLogTime = now;
                        }
                    } catch(e) {
                         // Silent fail to prevent crash in rapid CV loop
                    }
                }
            });
        } catch(err) {
            console.log("[-] FATAL: Failed to hook Vision properties - " + err.message);
        }
    } else {
        console.log("[-] WARNING: CoreML/Vision frameworks not loaded in current process.");
    }
}
