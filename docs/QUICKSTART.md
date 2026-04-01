# 🛡️ SENTINEL: THE ULTIMATE iOS BYPASS

![Sentinel Tactical Platform](./banner.png)

## 🏁 The 60-Second Infiltration Guide
*No complex setup. No headache. Just results.*

---

### **1️⃣  One-Click Dependency Fix**
Open your **Terminal** (Cmd + Space, type `Terminal`) and paste this line. It installs everything you need automatically.
```bash
pip install frida-tools pytest frida
```

### **2️⃣  Fire Up the Target**
1. Open your **iOS Simulator**.
2. Make sure the app **DummyBank** (or your target) is installed and visible.
3. Don't even open the app yet. Sentinel will do it for you.

### **3️⃣  Execute the Payload**
Paste this final command and watch the magic happen:
```bash
python3 -m pytest tests/v8_suite/test_suite_v8.py -v -s
```

---

## 🌈 What Happens Next? (The "Success" Sequence)

Once you hit enter, Sentinel will take over. Here is what you will see in your terminal:

| Stage | Status | Tactical Effect |
| :--- | :--- | :--- |
| **CLOAK** | ✅ ACTIVE | Your Simulator now looks like a clean iPhone 15 Pro. No JB traces. |
| **KEYCHAIN** | ✅ ARMED | Biometrics are bypassed. Every login attempt will return "SUCCESS." |
| **CAMERA** | ✅ HIJACKED | The app's camera is now showing our custom "Hacker" image. |

---

## 🆘 "It's Not Working!" (Panic Room)

> [!CAUTION]
> **If you see "No devices found":**
> 1. Close the Simulator. 
> 2. Open it again.
> 3. Run the command in Step 3.

> [!IMPORTANT]
> **If you see "Command not found":**
> You might need to use `python` instead of `python3`. Try both!

---

### 📖 Want to go deeper?
Check out the [Detailed Tactical Manual](./USAGE_GUIDE.md) to learn how to change photos, bundle IDs, and more.

---
*Developed by Kadir Arıcı & Sentinel Tactical Team*
