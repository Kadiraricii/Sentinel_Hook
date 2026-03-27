import frida
import sys
import time

def on_message(message, data):
    if message['type'] == 'send':
        print(f"📡 [SIGNAL] {message['payload']}")
    elif message['type'] == 'error':
        print(f"🚨 [ERROR] {message['stack']}")

def run_integration_test(target_process):
    print(f"🛰️  SENTINEL - Tam Entegrasyon Testi Başlatılıyor: {target_process}")
    try:
        device = frida.get_local_device()
    except:
        device = frida.get_usb_device()

    print(f"🔗 Cihaz Senkronize Edildi: {device.name}")
    
    try:
        session = device.attach(target_process)
        print(f"🎯 Hedef Kilitlendi: {target_process}")
        
        # 1. Tüm bypass dosyalarını bundle gibi birleştir (Basit birleştirme)
        hooks = [
            "src/hooks/ios/local_auth_bypass.js",
            "src/hooks/ios/camera_bypass.js",
            "src/hooks/ios/vision_bypass.js"
        ]
        
        combined_js = ""
        for hook in hooks:
            with open(hook, "r") as f:
                combined_js += f"\n// --- Hook: {hook} ---\n"
                combined_js += f.read()
        
        script = session.create_script(combined_js)
        script.on('message', on_message)
        script.load()
        
        print("\n🔥 [STATUS] TÜM MODÜLLER AKTİF!")
        print("💡 Lütfen uygulamada hem biyometrik girişi hem de liveness kamerasını test edin.")
        print("⌛ 60 saniye boyunca tam operasyon izleniyor...\n")
        
        time.sleep(60)
        session.detach()
        print("\n✅ Entegrasyon Testi Başarıyla Tamamlandı.")
        
    except Exception as e:
        print(f"\n❌ Kritik Hata: {str(e)}")

if __name__ == "__main__":
    target = "DummyBank" 
    run_integration_test(target)
