This script performs a **Framework-Level Video Injection**. It intercepts the raw data stream from the camera hardware before it reaches the application logic. 

By manipulating the `CMSampleBuffer`—the container for video frames in iOS—the script replaces the real-world camera feed with a static image, which is a common technique for bypassing **"Liveness Detection"** in facial recognition systems.

Here is the technical breakdown of the pipeline:

---

### 1. Image-to-Buffer Conversion (`_buildPixelBufferFromImage`)
The script first converts a standard image file (JPEG/PNG) into a format the iOS camera pipeline understands: `CVPixelBuffer`.
*   **The Transformation:** It uses `UIImage` to decode the file and `CGImage` to get the raw pixel data.
*   **The Allocation:** It calls `CVPixelBufferCreate` with the pixel format `0x42475241` (which is the Little Endian hex for **'BGRA'**). 
*   **Caching:** To ensure performance and avoid a massive memory leak, it caches the `_pixelBufferCache`. If it didn't, the script would try to re-decode the image 30 to 60 times per second (the frame rate of the camera), causing the app to crash.

### 2. The Sample Buffer Swap (`_swapSampleBuffer`)
This is the most critical technical part. A `CMSampleBuffer` isn't just an image; it is a complex structure containing the image, the video format description, and **precise timing information**.

*   **Timing Preservation:** If you simply provided a new image without timing data, the video stream would freeze or the app would crash because the "clock" of the video would stop.
*   **The Technique:**
    1.  It uses `CMSampleBufferGetFormatDescription` to steal the dimensions and color space data from the **original** camera frame.
    2.  It uses `CMSampleBufferGetSampleTimingInfoArray` to steal the **Presentation Time Stamp (PTS)** from the real frame. This ensures the "fake" frame appears at exactly the moment the "real" frame was supposed to.
    3.  It calls `CMSampleBufferCreateReadyWithImageBuffer` to forge a new buffer that combines your **fake pixels** with the **real metadata**.

### 3. Universal Delegate Hijacking (`attachCameraHook`)
iOS apps typically receive camera frames via a delegate method: `captureOutput:didOutputSampleBuffer:fromConnection:`.

*   **Discovery via `ObjC.choose`:** Instead of hooking a specific class (like `ViewController`), the script scans the entire heap for *any* object that implements that specific camera delegate selector. This makes the hook "universal"—it works on almost any app that uses `AVFoundation`.
*   **The Interception:**
    *   When the camera hardware produces a frame, it calls this delegate.
    *   The script's `onEnter` block fires first.
    *   `args[3]` corresponds to the third argument of the Objective-C method: the `CMSampleBuffer`.
    *   **The Swap:** The script overwrites `args[3]` with the pointer to its forged "hacker.jpg" buffer.

### 4. Why this is effective for Biometric Bypass
Most facial recognition SDKs (like those used in banking) operate in three steps:
1.  **Capture:** Get a frame from the camera.
2.  **Liveness Check:** Look for blinking or head movement.
3.  **Matching:** Compare the face to a database.

By injecting at the **Framework Level**, you are feeding the "fake" image into Step 1. Because the script preserves the **Timing Info**, the SDK's internal loop continues to run smoothly, thinking it is receiving a high-speed video feed of a person who just happens to be perfectly still.

### Summary of the "Ghost" Pipeline
1.  **Original State:** Camera $\rightarrow$ `AVFoundation` $\rightarrow$ App Logic.
2.  **Sentinel State:** 
    *   Camera $\rightarrow$ `AVFoundation` (Frame Created).
    *   **Sentinel Hook** $\rightarrow$ (Extract Timing, Discard Real Pixels, Insert "Hacker.jpg" Pixels).
    *   Sentinel Hook $\rightarrow$ App Logic (Receives "Hacker.jpg" with perfect timing metadata).