"""
Phase 8 — Tactical Test Suite
tests/v8_suite/test_suite_v8.py

Automated verification for Cloak, Keychain, and Camera modules.
"""

import frida
import pytest
import time
import sys

@pytest.fixture(scope="session")
def frida_session():
    bundle_id = "keydo.DummyBank" # Projenin ana hedefi
    # Tam UUID: 8C98828E-BAC8-4D91-AE1B-5F9E4C2B26BC
    try:
        device = frida.get_device('8C98828E-BAC8-4D91-AE1B-5F9E4C2B26BC')
    except:
        device = frida.get_device_matching(lambda d: "iPhone 17 Pro" in d.name)

    print(f"[TEST] Cihaz Seçildi: {device.name}")
    
    pid = device.spawn([bundle_id])
    session = device.attach(pid)
    
    # Bağımlılıkları inline et (Frida require desteklemez)
    def read_hook(name):
        with open(f"src/hooks/ios/{name}.js", "r") as f:
            content = f.read()
            # module.exports satırlarını temizle
            return content.replace("module.exports =", "// module.exports =")

    cloak_src = read_hook("cloak_hook")
    keychain_src = read_hook("keychain_hook")
    camera_src = read_hook("camera_hook")

    with open("src/sentinel_loader.js", "r") as f:
        loader_lines = f.readlines()
        
    # require satırlarını tamamen sil (Global scope'ta zaten varlar)
    clean_loader_lines = []
    for line in loader_lines:
        if 'require("' in line:
            clean_loader_lines.append(f"// {line.strip()} (inlined)\n")
        else:
            clean_loader_lines.append(line)
    
    loader_src = "".join(clean_loader_lines)

    full_src = (
        "try {\n"
        "    console.log('[SENTINEL] Core boot sequence started...');\n"
        + cloak_src + "\n"
        "    console.log('[SENTINEL] Cloak modules loaded.');\n"
        + keychain_src + "\n"
        "    console.log('[SENTINEL] Keychain modules loaded.');\n"
        + camera_src + "\n"
        "    console.log('[SENTINEL] Camera modules loaded.');\n"
        + loader_src + "\n"
        "    console.log('[SENTINEL] Central loader initialized.');\n"
        "} catch (e) {\n"
        "    send({ type: 'error', stack: e.stack, message: e.message });\n"
        "}\n"
    )

    script = session.create_script(full_src)
    
    def on_message(message, data):
        if message['type'] == 'send':
            payload = message['payload']
            if isinstance(payload, dict) and payload.get('type') == 'error':
                print(f"[FRIDA FATAL] {payload.get('stack')}")
            else:
                print(f"[FRIDA] {payload}")
        elif message['type'] == 'error':
            print(f"[FRIDA ERROR] {message['stack']}")

    script.on('message', on_message)
    script.load()
    
    device.resume(pid)
    time.sleep(5) 
    
    yield script, device, pid
    session.detach()

def test_sentinel_ping(frida_session):
    script, _, _ = frida_session
    try:
        result = script.exports_sync.ping()
        assert result == "pong"
    except Exception as e:
        pytest.fail(f"RPC ping failed: {e}")

def test_sentinel_config_resolution(frida_session):
    script, _, _ = frida_session
    try:
        cfg = script.exports_sync.get_config()
        assert "cloak" in cfg
        assert "keychain" in cfg
        assert "camera" in cfg
        assert cfg["cloak"]["spoofedModel"] == "iPhone 15 Pro"
    except Exception as e:
        pytest.fail(f"RPC getConfig failed: {e}")

def test_stealth_integrity(frida_session):
    script, _, _ = frida_session
    try:
        cfg = script.exports_sync.get_config()
        assert cfg["cloak"]["logBlockedPaths"] is True
    except Exception as e:
        pytest.fail(f"RPC check failed: {e}")
