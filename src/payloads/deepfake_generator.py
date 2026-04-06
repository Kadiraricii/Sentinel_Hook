#!/usr/bin/env python3
"""
Sentinel Hook - Phase 10.1 (PoC Deepfake Pipeline)
Lightweight OpenCV-based face overlay generator.

Usage:
  python3 deepfake_generator.py --video source.mp4 --face target.jpg --output .local/test-videos/faceswap_frames/
"""

import cv2
import numpy as np
import argparse
import os
import urllib.request
import time

def download_cascade():
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    filename = "haarcascade_frontalface_default.xml"
    if not os.path.exists(filename):
        print(f"[*] Downloading Face Detection Cascade ({filename})...")
        urllib.request.urlretrieve(url, filename)
    return filename

def overlay_transparent(background, overlay, x, y):
    """
    Overlays a transparent image or merges bounding boxes.
    Since target might be a generic JPG, we just resize and overlay.
    """
    bg_h, bg_w, set_c = background.shape
    h, w, c = overlay.shape

    if x >= bg_w or y >= bg_h:
        return background

    h = min(h, bg_h - y)
    w = min(w, bg_w - x)
    
    overlay_cropped = overlay[0:h, 0:w]
    background[y:y+h, x:x+w] = overlay_cropped
    return background

def run_deepfake_pipeline(video_path, target_face_path, output_dir):
    print(f"[*] Starting Sentinel Deepfake Engine (PoC)")
    
    cascade_path = download_cascade()
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Load target face
    if not os.path.exists(target_face_path):
        print(f"[!] Error: Target face '{target_face_path}' not found. Using black box fallback.")
        target_face = np.zeros((200, 200, 3), dtype=np.uint8)
    else:
        target_face = cv2.imread(target_face_path)

    # Open video
    if not os.path.exists(video_path):
        print(f"[!] Error: Video '{video_path}' not found. Cannot proceed.")
        return

    cap = cv2.VideoCapture(video_path)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_count = 0
    print("[*] Processing Video Stream...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect face
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            # Resize target face to fit tracked box
            resized_face = cv2.resize(target_face, (w, h))
            
            # Apply smooth blending to margins
            # Fast PoC: Direct Replacement
            frame = overlay_transparent(frame, resized_face, x, y)
            
            # Annotate tracking
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "DEEPFAKE [LOCKED]", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # Output to Sentinel frame pipeline
        out_path = os.path.join(output_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(out_path, frame)
        
        if frame_count % 30 == 0:
            print(f"   -> Processed {frame_count} frames...")
            
        frame_count += 1
        
    cap.release()
    print(f"[+] Total {frame_count} deepfake frames rendered to '{output_dir}'.")
    print("[+] Sentinel Hook can now intercept CVPixelBuffer using these frames!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentinel Hook - Deepfake PoC Pipeline")
    parser.add_argument("--video", type=str, default="sample.mp4", help="Source target video.")
    parser.add_argument("--face", type=str, default="hacker.jpg", help="Hacker face to inject.")
    parser.add_argument("--output", type=str, default=".local/test-videos/faceswap_frames/", help="Output directory.")
    
    args = parser.parse_args()
    run_deepfake_pipeline(args.video, args.face, args.output)
