import frida
import json
import sys

def list_devices():
    try:
        devices = []
        for device in frida.enumerate_devices():
            if device.id in ["socket", "barebone"]:
                continue
                
            # Cihaz tipini daha anlasilir hale getir
            d_type = device.type
            if device.id.startswith("8C98") or "-" in device.id and len(device.id) > 20: 
                # Simülatör tespiti (basit mantik: uzun ID ve simulatöre özel patternler)
                if d_type == "local" or d_type == "remote":
                    d_type = "simulator"

            devices.append({
                "id": device.id,
                "name": device.name,
                "device_type": d_type
            })
        print(json.dumps(devices))
    except Exception as e:
        print(json.dumps([]))

if __name__ == "__main__":
    list_devices()
