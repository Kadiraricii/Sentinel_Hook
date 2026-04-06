# Hook Reference — Sentinel Hook

> Complete reference for all Frida injection modules, their hook surfaces, and expected behaviors.

---

## Module Registry

| Module ID | Script(s) | Layer | Swift Bridge Method |
|---|---|---|---|
| `biometrics` | `local_auth_bypass.js` | ObjC — LAContext | — (direct callback) |
| `camera` | `camera_bypass.js`, `video_replayer.js` | ObjC — AVFoundation | `sentinelCameraBypass()` |
| `vision` | `vision_bypass.js`, `opencv_bypass.js` | ObjC — Vision + C++ | `sentinelVisionBypass()` |
| `security` | `frida_detection_bypass.js` | C — syscall + DYLD | `sentinelSecurityBypass()` |
| `mfachain` | `mfa_chain_bypass.js` | ObjC — LAContext + Swift | `verifyOTP(code:)` arg replace |
| `deepfake` | `realtime_deepfake_hook.js`, `kernel_camera_hook.js` | ObjC + C | `sentinelKernelBypass()` |
| `kernelcam` | `kernel_camera_hook.js`, `realtime_deepfake_hook.js` | C + ObjC | `sentinelKernelBypass()` |

---

## 1. Biometrics — `local_auth_bypass.js`

```
Target:  LAContext.canEvaluatePolicy   (ObjC)
         LAContext.evaluatePolicy       (ObjC)
```

**Technique:** `canEvaluatePolicy` is hooked in `onLeave` to replace `retval` with `1` (YES). `evaluatePolicy` is hooked in `onEnter` to immediately fire the Swift `reply` block with `success = true, error = nil` before the system can reject it.

**Why `onEnter` not `onLeave`:** On simulator, the system never reaches `onLeave` for `evaluatePolicy` because there is no hardware to evaluate. Firing the reply in `onEnter` guarantees execution regardless of hardware availability.

**Swift surface:** `BiometricAuthManager.authenticateUser()` — `@objc dynamic`. The `asyncAfter` retry on simulator gives Frida 0.8s to register the hook before the second `LAContext` call.

**Success indicator:** `authManager.isAuthenticated = true` → ContentView routes to `.compromised`.

---

## 2. Camera — `camera_bypass.js` + `video_replayer.js`

```
Target:  _TtC9DummyBank13CameraManager.simulateFrameTrigger  (ObjC)
         _TtC9DummyBank13CameraManager.sentinelCameraBypass  (ObjC, Frida bridge)
```

**Technique:** `simulateFrameTrigger` is the periodic frame dispatch method instrumented as the injection point. The hook calls `receiveHackerImage:` with a synthetic JPEG path. `ObjC.chooseSync()` finds the live `CameraManager` instance and calls `sentinelCameraBypass()` directly.

**Swift surface:** `CameraManager.sentinelCameraBypass()` — `@objc dynamic`. Sets `isCameraAuthenticated = true` on the main thread.

**Success indicator:** `cameraManager.isCameraAuthenticated = true` → ContentView routes to `.compromised(message: "TARGET B: ...")`.

---

## 3. Vision — `vision_bypass.js` + `opencv_bypass.js`

```
Target:  VNDetectFaceRectanglesRequest.results  (ObjC property getter)
         dlopen (OpenCV DNN — C, physical devices only)
```

**Technique:** The `results` property getter is hooked in `onLeave` to replace its return value with a pre-allocated `NSArray` containing a synthetic `VNFaceObservation`. The observation is `.retain()`-ed to prevent Frida's garbage collector from freeing it between calls.

**Simulator note:** `opencv_bypass.js` uses `dlopen` which is unavailable on simulator — it is gracefully skipped. The ObjC `vision_bypass.js` hook works on both.

**Swift surface:** `CameraManager.sentinelVisionBypass()` — sets `isCameraAuthenticated = true` and `aiFaceDetected = true`.

---

## 4. Security — `frida_detection_bypass.js`

```
Target:  open()   (C — libc, FS probe masking)
         sysctl   (C — kernel, anti-debug, physical devices only)
         _TtC9DummyBank20SecurityCheckManager.sentinelSecurityBypass  (ObjC bridge)
```

**Technique:** `open()` path argument is inspected in `onEnter`; if it contains `frida` or `cydia`, the path is overwritten with `/dev/null` before the kernel sees it. On physical devices, `sysctl` `CTL_KERN_PROC_PROC` is intercepted to suppress the `P_TRACED` (debugger attached) flag.

**Simulator:** `sysctl` and `open()` hooks are silently skipped with an informative log; no error messages are emitted. The ObjC bridge call still fires.

**Swift surface:** `SecurityCheckManager.sentinelSecurityBypass()` — sets `sentinelMaskActive = true` and rewrites the `DYLD: frida-agent.dylib` finding to show `MASKED by Sentinel stealth layer`.

---

## 5. MFA Chain — `mfa_chain_bypass.js`

```
Target:  LAContext.evaluatePolicy                         (Phase 1 re-used)
         _TtC9DummyBank14MFAAuthManager.verifyOTP_code_  (ObjC mangled)
```

**Technique (Chain):**
1. `LAContext.evaluatePolicy` hook fires the biometric success callback — same as module 1
2. `verifyOTP(code:)` is hooked in `onEnter`:
   - `args[2]` (the OTP string `NSString*`) is replaced with a new `NSString` containing `SENTINEL_OVERRIDE`
   - `retval` in `onLeave` is forced to `1` as a safety double-tap
3. The Swift method checks `code == "SENTINEL_OVERRIDE"` → returns `true` → `isFullyAuthenticated = true`

**Without injection:** `verifyOTP` rejects any code that does not match the randomly generated expected OTP printed to the Xcode console.

**Swift surface:** `MFAAuthManager.verifyOTP(code:)` — `@objc dynamic`.

---

## 6. Deepfake — `realtime_deepfake_hook.js`

```
Target:  _TtC9DummyBank13CameraManager  (ObjC instance, CVPixelBuffer pipeline)
```

**Technique:** Emits synthetic `CVPixelBuffer`-level frame tags at 5-frame intervals simulating a deepfake pipeline replacement. On physical devices with `AVCaptureVideoDataOutput`, actual buffer swapping can be performed.

**FRAME tags emitted:** `[FRAME:CVPixelBuffer:timestamp:SYNTHETIC]`

---

## 7. Kernel Camera Hook — `kernel_camera_hook.js`

```
Target (L1):  IOSurface + surfaceWithProperties:  (ObjC)
Target (L2):  CMSampleBufferCreateReadyWithImageBuffer  (CoreMedia C export)
              AVCaptureSession.startRunning  (ObjC fallback for simulator)
Target (L3):  VTCompressionSessionEncodeFrame  (VideoToolbox C export)
              CVPixelBufferLockBaseAddress  (CoreVideo C export fallback)
```

**Technique:** Three independent interceptors target progressively deeper layers of the iOS camera pipeline, below the `AVFoundation` API surface. On simulator, C exports that are unavailable fall back to the deepest accessible ObjC method.

**Heartbeat:** `setInterval` emits `[FRAME:KERNEL_HEARTBEAT:timestamp:ACTIVE]` every 1500ms to keep the dashboard Live Sensor Feed panel animated.

**Swift surface:** `CameraManager.sentinelKernelBypass()` — `@objc dynamic`. Called via `ObjC.chooseSync()`.

---

## Frida–Swift Bridge Pattern

All camera and security modules use the following pattern to trigger Swift UI updates:

```javascript
var instances = ObjC.chooseSync(ObjC.classes["_TtC9DummyBank13CameraManager"]);
if (instances.length > 0) {
    instances[0]["- sentinelCameraBypass"]();
}
```

If no live instance is found (target screen not yet opened), the hook falls back to intercepting `startDummySessionForSimulator` — the method called when any camera-related target button is tapped — and fires the bypass from there.

---

## FRAME Tag Protocol (Phase 10.4)

Hooks emit structured log lines that the dashboard WebSocket parser consumes without displaying them in the console:

```
[FRAME:LAYER:TIMESTAMP_MS:STATUS]

Examples:
[FRAME:IOSURFACE:1712345678901:INTERCEPTED]
[FRAME:SAMPLEBUFFER:1712345678910:TAGGED]
[FRAME:VTCOMPRESSION:1712345678920:ENCODED]
[FRAME:KERNEL_HEARTBEAT:1712345678930:ACTIVE]
[FRAME:CVPIXELBUFFER:1712345678940:LOCKED]
```

The dashboard extracts `LAYER` for the "Last Layer" display and increments a frame counter.
