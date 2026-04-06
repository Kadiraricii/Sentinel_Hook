# Changelog — Sentinel Hook

All notable changes to this project are documented in this file.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [10.4.1] — 2026-04-06

### Fixed
- `frida_detection_bypass.js`: Suppressed `sysctl / open() — not a function` simulator errors; replaced with informative passive-mode messages
- Dashboard console auto-scroll no longer scrolls the entire page; scroll is now contained within the terminal panel using `scrollTop` instead of `scrollIntoView`
- `ContentView.swift`: Added missing `import Combine` required for `ObservableObject` conformance in `SecurityCheckManager`
- `ContentView.swift`: Fixed missing `message:` argument label on `.compromised()` enum case call sites
- `ContentView.swift`: Resolved `\\\"` escaped-quote syntax error left by a previous edit

### Added
- `SecurityCheckManager.sentinelSecurityBypass()`: Frida-callable `@objc dynamic` method that marks the Frida DYLD finding as MASKED in real-time without re-running the full scan

---

## [10.4.0] — 2026-04-06

### Added — Phase 10.4: Remote Control Panel & Live Sensor Feed
- Dashboard **Live Sensor Feed** panel with animated scan-line viewport, crosshair overlay, and real-time frame counter
- `[FRAME:LAYER:timestamp:STATUS]` WebSocket tag protocol — hooks emit tags, dashboard parses them and updates panel state without polluting the console log
- Panel activates automatically when CAMERA, DEEPFAKE, or KERNEL CAM modules are toggled on

---

## [10.3.0] — 2026-04-06

### Added — Phase 10.3: Kernel-Level Camera Hooking
- `src/hooks/advanced/kernel_camera_hook.js`: Three-layer kernel-boundary camera pipeline hook
  - **L1** — `IOSurface` ObjC class (GPU shared memory allocation)
  - **L2** — `CMSampleBufferCreateReadyWithImageBuffer` C export / `AVCaptureSession` ObjC fallback
  - **L3** — `VTCompressionSessionEncodeFrame` / `CVPixelBufferLockBaseAddress` fallback
- Simulator-safe: all fallbacks use ObjC methods when C exports are unavailable
- 1.5-second heartbeat emitting `[FRAME:KERNEL_HEARTBEAT:...]` tags for live feed animation
- `CameraManager.sentinelKernelBypass()`: Frida entry point → sets `isCameraAuthenticated = true`
- Dashboard: **KERNEL CAM HOOK** module card (green, `Radio` icon)
- DummyBank: **Target G — Kernel Camera Hook** button (green border)
- `inject_hooks.py`: `kernelcam` module key registered

---

## [10.2.1] — 2026-04-06

### Changed
- `MFAAuthManager.initiateMFAChain()`: On simulator where biometric hardware is unavailable, the OTP screen is always shown (after 0.6s delay) to enable the MFA bypass demo without a physical device
- `MFAAuthManager.verifyOTP()`: Wrong codes are now strictly rejected (`❌ Wrong code`) without injection; only the exact OTP or Frida-injected `SENTINEL_OVERRIDE` god-key is accepted
- OTP screen: Added 6-digit auto-submit on `onChange`; SUBMIT CODE / ABORT buttons; purple status banner indicating when Sentinel is active

---

## [10.2.0] — 2026-04-05

### Added — Phase 10.2: MFA Chain Bypass
- `src/hooks/05_mfa/mfa_chain_bypass.js`: Chains `LAContext.evaluatePolicy` bypass with `MFAAuthManager.verifyOTP` interception; replaces OTP argument with `SENTINEL_OVERRIDE` god-key
- `tests/DummyBank/MFAAuthManager.swift`: Full OTP delivery simulation; `@objc dynamic verifyOTP(code:)` is the Frida hook surface
- DummyBank: **Target E — MFA Vault** with `awaitingOTP` state routing and OTP input screen
- Dashboard: **MFA CHAIN BYPASS** module (magenta, `Activity` icon)

---

## [10.1.0] — 2026-04-05

### Added
- Pattern lock interception hooks
- Combined Face ID + Pattern Lock bypass chain
- DummyBank phase 10.1 test surface

---

## [9.0.0] — 2026-04-04

### Added — Rust Backend & React Dashboard
- Rust Axum WebSocket server (`sentinel-rust/`) for real-time hook orchestration
- React + Vite tactical dashboard (`web_ui/`) with:
  - Device discovery panel (USB & simulator)
  - Per-module toggle switches
  - Live terminal with CLEAR button
  - PURGE SESSIONS for global hook detach
  - `NUCLEAR PURGE` — detaches all active hooks

### Changed
- `inject_hooks.py`: Migrated from subprocess-per-module to Rust-managed PID registry; detach now sends single-module payload instead of full purge

---

## [8.0.0] — 2026-04-04

### Added — Anti-Analysis & Orchestration
- `_sentinel_bundle.js`: Multi-file bundler for combined injection payloads
- `inject_hooks.py`: Module registry (`biometrics`, `camera`, `vision`, `security`, `deepfake`, `mfachain`, `kernelcam`, `all`)
- Sentinel Protocol v8.0 log headers

---

## [7.0.0] — 2026-04-03

### Added — Deepfake Pipeline + Video Replay
- `realtime_deepfake_hook.js`: Synthetic CV frame injection into `CVPixelBuffer` at 5-frame intervals
- `video_replayer.js`: Pre-recorded session frame replay via `AVCaptureSession` output

---

## [5.0.0] — 2026-04-02

### Added — Anti-Tamper Shield
- `frida_detection_bypass.js`: `open()` hook redirects jailbreak/Frida paths to `/dev/null`; `sysctl` P_TRACED flag masking on physical devices

---

## [4.0.0] — 2026-04-02

### Added — OpenCV Native Bypass
- `opencv_bypass.js`: `dlopen` hook for OpenCV DNN native layer; simulator passive mode

---

## [3.0.0] — 2026-04-01

### Added — AI Vision Spoofing
- `vision_bypass.js`: `VNDetectFaceRectanglesRequest.results` override with persistent `VNFaceObservation` (`.retain()` to survive Frida GC)

---

## [2.0.0] — 2026-03-31

### Added — Camera Hijacking
- `camera_bypass.js`: `simulateFrameTrigger` hook + `receiveHackerImage:` synthetic frame pipeline
- `CameraManager.sentinelCameraBypass()`: `@objc dynamic` Swift entry point

---

## [1.0.0] — 2026-03-30

### Added — Initial Release
- `local_auth_bypass.js`: `LAContext.canEvaluatePolicy` and `evaluatePolicy` hooks
- `BiometricAuthManager.swift`: `asyncAfter` retry logic for simulator compatibility
- DummyBank initial targets A, B, C
