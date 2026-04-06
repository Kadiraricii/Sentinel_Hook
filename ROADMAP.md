# Roadmap — Sentinel Hook

> This document tracks the complete phased development plan for the Sentinel Hook academic research framework.

---

## Legend

| Icon | Meaning |
|---|---|
| ✅ | Completed |
| 🔄 | In Progress |
| 📋 | Planned |

---

## Phase 1 — Biometric Authentication Bypass

**Target:** `LAContext.evaluatePolicy` (Face ID / Touch ID)

- ✅ Hook `LAContext.canEvaluatePolicy` → spoof hardware availability
- ✅ Hook `LAContext.evaluatePolicy` → force `success = true` in `onEnter`
- ✅ Simulator-safe detection via `UIDevice.currentDevice().model()`
- ✅ DummyBank **Target A: Face ID Gate** wired to `BiometricAuthManager`

---

## Phase 2 — Camera Feed Hijacking

**Target:** `AVCaptureSession`, `AVCaptureVideoDataOutput`

- ✅ Hook `simulateFrameTrigger` to intercept live frame dispatch
- ✅ Inject synthetic JPEG via `receiveHackerImage:` backdoor method
- ✅ `sentinelCameraBypass()` bridge → sets `isCameraAuthenticated = true`
- ✅ DummyBank **Target B: Raw Camera Feed**

---

## Phase 3 — AI / ML Liveness Detection Spoofing

**Target:** `VNDetectFaceRectanglesRequest`, CoreML

- ✅ Hook `VNDetectFaceRectanglesRequest.results` → replace with synthetic `VNFaceObservation`
- ✅ Persistent object retention via `.retain()` to survive Frida GC cycles
- ✅ `sentinelVisionBypass()` bridge → sets `aiFaceDetected = true`
- ✅ DummyBank **Target C: Liveness Scan**

---

## Phase 4 — OpenCV Native Bypass

**Target:** OpenCV DNN C++ native layer

- ✅ `dlopen` hook for OpenCV dynamic library (physical devices)
- ✅ Simulator passive mode with documented fallback behavior
- ✅ Integrated into VISION module alongside `vision_bypass.js`

---

## Phase 5 — Anti-Tamper & Frida Detection Masking

**Target:** `sysctl`, `open()`, DYLD image list

- ✅ `open()` hook redirects jailbreak file paths to `/dev/null`
- ✅ DYLD scan surface exposed in Swift via `SecurityCheckManager`
- ✅ `sentinelSecurityBypass()` bridge → marks Frida as MASKED in scan results
- ✅ Simulator-aware: kernel hooks gracefully suppressed with informative messages
- ✅ DummyBank **Target D: Anti-Tamper Core**

---

## Phase 6 — Deepfake Pipeline

**Target:** `CVPixelBuffer` injection

- ✅ `realtime_deepfake_hook.js` — synthetic CV frame injection at 5-frame intervals
- ✅ Emits `[FRAME:CVPixelBuffer:...]` tags for dashboard live feed
- ✅ DummyBank **Target F: Deepfake Neural-Link**

---

## Phase 7 — Video Replay Attack

**Target:** `AVCaptureSession` output replay

- ✅ `video_replayer.js` — loops pre-recorded session frames into the live capture output
- ✅ Bundled with CAMERA module

---

## Phase 8 — Anti-Analysis & Orchestration

- ✅ `_sentinel_bundle.js` — automatic multi-file bundler for combined injection
- ✅ `inject_hooks.py` — module registry with PID tracking and per-module detach
- ✅ NUCLEAR PURGE — detaches all hooks simultaneously

---

## Phase 9 — Rust Backend & React Dashboard

**Tech:** Axum WebSocket server + React + Vite

- ✅ Real-time log streaming over WebSocket (`ws://127.0.0.1:8000/ws`)
- ✅ Device discovery via `frida-core` bindings
- ✅ Per-module toggle switches (not buttons) with active/inactive state
- ✅ Console auto-scroll contained within terminal panel (does not scroll page)
- ✅ CLEAR button for terminal log purge
- ✅ PURGE SESSIONS — global hook detach

---

## Phase 10.1 — Pattern Lock & Combo Auth Bypass

- ✅ Pattern lock interception hooks
- ✅ Face ID + Pattern lock combined chain bypass

---

## Phase 10.2 — MFA Chain Bypass

**Target:** `MFAAuthManager.verifyOTP` + LAContext chain

- ✅ `mfa_chain_bypass.js` — intercepts `verifyOTP(code:)` and replaces `args[2]` with `SENTINEL_OVERRIDE`
- ✅ `initiateMFAChain()` — biometric → OTP two-step chain with simulator fallback
- ✅ OTP auto-submit on 6-digit entry; wrong codes rejected without injection
- ✅ DummyBank **Target E: MFA Vault** with `awaitingOTP` state routing
- ✅ OTP screen hint badge shows "SENTINEL ACTIVE → ANY CODE BYPASSES"

---

## Phase 10.3 — Kernel-Level Camera Hooking

**Target:** `IOSurface`, `CMSampleBuffer`, `VTCompressionSession`

- ✅ L1: `IOSurface` ObjC allocation hook (GPU shared memory boundary)
- ✅ L2: `CMSampleBufferCreateReadyWithImageBuffer` / `AVCaptureSession` fallback
- ✅ L3: `VTCompressionSessionEncodeFrame` / `CVPixelBufferLockBaseAddress` fallback
- ✅ `sentinelKernelBypass()` bridge → triggers COMPROMISED screen
- ✅ `[FRAME:KERNEL_HEARTBEAT:...]` tags emitted every 1.5s for live feed animation
- ✅ DummyBank **Target G: Kernel Camera Hook**

---

## Phase 10.4 — Remote Control Panel & Live Sensor Feed

- ✅ Dashboard Live Sensor Feed panel (Phase 10.4)
- ✅ `[FRAME:LAYER:timestamp:STATUS]` WebSocket tag parsing
- ✅ Animated scan-line viewport with crosshair overlay and frame counter
- ✅ Panel activates automatically when CAMERA / DEEPFAKE / KERNEL CAM modules are on
- ✅ Remote hook toggle and detach (all existing dashboard functionality)

---

## Phase 10.5 — AI-Assisted Target Analysis

**Goal:** Automatic hook strategy recommendation based on target app characteristics

- 🔄 Pattern matching for known protection mechanisms (e.g. AppShield, FreeRASP)
- 📋 Automated hook script generation from binary analysis
- 📋 Integration with static analysis outputs (Ghidra / class-dump)

---

## Phase 11 — Cross-Platform Extension (Planned)

- 📋 Android support: Frida hooks for BiometricPrompt + CameraX
- 📋 V4L2 (Linux) driver-level camera hook research
- 📋 Automated APK unpacking + smali-level hook injection

---

<div align="center">
  <sub>Sentinel Hook · Academic Security Research · İstinye Üniversitesi · 2025–2026</sub>
</div>
