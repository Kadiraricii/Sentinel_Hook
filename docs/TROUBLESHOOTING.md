# Troubleshooting Guide — Sentinel Hook

> Common issues, root causes, and verified solutions.

---

## Table of Contents

- [Backend / Connection Issues](#backend--connection-issues)
- [Frida Injection Errors](#frida-injection-errors)
- [DummyBank / Simulator Issues](#dummybank--simulator-issues)
- [Dashboard / UI Issues](#dashboard--ui-issues)
- [Module-Specific Issues](#module-specific-issues)

---

## Backend / Connection Issues

### `No devices found` in dashboard

**Cause:** Frida server is not running, or the simulator is not booted.

**Fix:**
1. Ensure the iOS Simulator is running (launch DummyBank from Xcode first)
2. Verify `cargo run` is running in `sentinel-rust/`
3. Click **Scan Devices** — simulators are found via `frida-core` locally (no USB needed)

---

### `WebSocket connection failed`

**Cause:** Rust backend is not running or crashed on startup.

**Fix:**
```bash
cd sentinel-rust
source ../.venv/bin/activate
cargo run
```
Check for port conflicts: `lsof -i :8000`

---

### Module activates but immediately shows `oturumu kapandı`

**Cause:** Frida script crashes at load time (syntax error or missing ObjC class).

**Fix:** Check the terminal log for `[-] FATAL` or `not a function` lines immediately after `[*] filename.js yüklendi`.

---

## Frida Injection Errors

### `[-] STEALTH ERROR: sysctl - not a function`
### `[-] STEALTH ERROR: open() - not a function`

**Cause:** These are kernel-level C function hooks that require a physical iOS device. On the simulator (which runs as a macOS process), they are not available.

**Status:** ✅ Fixed in v10.4.1 — these are now silently skipped with an informational message. If you still see them, the bundled script is cached. Run:
```bash
python3 inject_hooks.py rebuild
```

---

### `[-] KERNEL L2: CMSampleBuffer hook failed - not a function`
### `[-] KERNEL L3: VTCompressionSession hook failed - not a function`

**Cause:** `Module.findExportByName("CoreMedia", ...)` returns `null` on simulator because the framework is loaded from a different path. The code was attempting to call `.isNull()` on a JavaScript `null`.

**Status:** ✅ Fixed in v10.3.0 — multiple symbol names are tried in sequence (`CMSampleBufferCreateReadyWithImageBuffer`, `CMSampleBufferCreate`, `CMSampleBufferGetImageBuffer`). If none are found, the hook falls back to `AVCaptureSession.startRunning` (L2) and `CVPixelBufferLockBaseAddress` (L3).

---

### `ObjC.chooseSync is empty — bypass not triggered`

**Cause:** The camera screen in DummyBank has not been opened yet, so no `CameraManager` instance exists in memory.

**Fix:** The fallback hook on `startDummySessionForSimulator` handles this — tap the target button in DummyBank after enabling the module. The bypass fires at session start.

---

### Script loads twice / hooks fire multiple times

**Cause:** `inject_hooks.py` is loading all JS files in a directory, including both `kernel_camera_hook.js` and `realtime_deepfake_hook.js` for both `deepfake` and `kernelcam` modules (they share `src/hooks/advanced/`).

**Impact:** Minor — duplicate log lines. Hook behavior is idempotent (the second hook on the same method is handled by Frida's interceptor stack).

---

## DummyBank / Simulator Issues

### `Could not create inference context` (Vision error loop)

**Cause:** `Vision.framework` face detection requests use the Neural Engine, which is not available on iOS Simulator. Each failed VNDetect request logs this error.

**Fix:** This is expected behavior on simulator. The `vision_bypass.js` hook still fires on the ObjC property getter, which short-circuits the pipeline before the result is consumed by app code. The error is from the underlying Vision framework and cannot be suppressed without disabling Vision entirely.

**Workaround:** Use a physical device for Vision module demonstrations without this noise.

---

### Biometric bypass fires but app screen doesn't update

**Cause:** `BiometricAuthManager.authenticateUser()` was called before the Frida hook was registered; the hook missed the window.

**Fix:** The retry logic in `BiometricAuthManager` waits 0.8s on simulator before calling `LAContext` a second time. If you toggle the module and then immediately tap Target A, the hook should be in place.

Ensure module shows `[OK] Modül 'biometrics' aktif edildi` in the terminal *before* tapping.

---

### MFA OTP screen: wrong code is accepted without injection

**Cause:** Old code had `code == "SENTINEL_OVERRIDE"` hardcoded in Swift, making it pass regardless of Frida.

**Status:** ✅ Fixed in v10.2.1 — `verifyOTP` now only accepts the randomly generated OTP (logged to Xcode console) or the Frida-injected god-key. Wrong codes produce `❌ Wrong code`.

---

### Target D (Anti-Tamper) shows Frida as `NOT PRESENT` even without Security module

**Cause:** `_dyld_image_count` / `_dyld_get_image_name` may not expose `frida-agent` under all Frida attachment modes.

**Expected behavior:** On simulator without injection, Frida is typically **detected** (showing `⚠ INJECTED`). With DETECTION SHIELD active, it shows `✅ MASKED`. If Frida is not detected initially, the demonstration still works — enable the module and re-run Target D scan to observe the `sentinelSecurityBypass()` call updating the result in real-time.

---

## Dashboard / UI Issues

### Page scrolls to bottom when new logs arrive

**Status:** ✅ Fixed in v10.4.1 — the log stream now uses `consoleRef.current.scrollTop = scrollHeight` instead of `element.scrollIntoView()`. Only the terminal panel scrolls internally.

---

### Module toggle turns on but doesn't turn off cleanly

**Cause:** Older builds sent an empty `modules` array on detach, causing the backend to interpret it as "attach all".

**Status:** ✅ Fixed — detach now sends a single-module payload `{ modules: [id], action: "detach" }`.

---

### Live Sensor Feed shows `[ NO SENSOR SIGNAL ]` even with KERNELCAM on

**Cause:** The dashboard parses `[FRAME:...]` messages from the WebSocket stream. If the heartbeat is not emitting, the panel stays idle.

**Fix:**
1. Confirm `kernel_camera_hook.js` loaded (check console for `KERNEL LAYER 2 (Simulator): AVCaptureSession boundary hooked`)
2. Open Target G in DummyBank to start the camera session
3. The `setInterval` heartbeat fires every 1500ms regardless of camera state — frames should appear within 2 seconds of module activation

---

## Module-Specific Issues

### DEEPFAKE module: `Frames intercepted: 0`

**Cause:** L1 IOSurface hook is looking for the class `IOSurface` which may not be loaded in the simulator process. This is cosmetic — frame count increments only when IOSurface is used by the real camera hardware.

**Impact:** None. Deepfake synthetic frame injection (`realtime_deepfake_hook.js`) runs independently via its own timer interval.

---

### Camera bypass fires but `isCameraAuthenticated` stays `false`

**Cause:** `ObjC.chooseSync` found no live `CameraManager` instance at injection time, and the fallback hook on `startDummySessionForSimulator` didn't fire because the camera screen was never opened.

**Fix:** Always toggle the injection module *before* pressing the corresponding target button in DummyBank, not after.
