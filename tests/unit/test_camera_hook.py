import frida
import sys
import time

def on_message(message, data):
    if message['type'] == 'send':
        print(f"[*] CAMERA SIGNAL: {message['payload']}")
    elif message['type'] == 'error':
        print(f"[!] ERROR: {message['stack']}")

def run_test(target_process):
    print(f"[INIT] Başlatılıyor: {target_process}")
    try:
        device = frida.get_local_device() # Simülatör için
    except:
        device = frida.get_usb_device()

    print(f"[*] Cihaz Bağlandı: {device.name}")
    
    try:
        session = device.attach(target_process)
        print(f"[✓] Süreç Yakalandı: {target_process}")
        
        # Kamera bypass dosyasını oku
        with open("src/hooks/ios/camera_bypass.js", "r") as f:
            js_code = f.read()
        
        script = session.create_script(js_code)
        script.on('message', on_message)
        script.load()
        
        print("[🌟] TEST BAŞLADI: Lütfen uygulamada kamerayı açın.")
        print("[!] 45 saniye boyunca kare (frame) yakalama izleniyor...")
        
        time.sleep(45)
        session.detach()
        print("[✓] Kamera Testi Tamamlandı.")
        
    except Exception as e:
        print(f"[!] Kamera Testi Başarısız: {str(e)}")

if __name__ == "__main__":
    target = "DummyBank" 
    run_test(target)
