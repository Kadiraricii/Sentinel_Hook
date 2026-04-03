# 🔧 Sentinel Hook — Sorun Giderme Rehberi

> **Kapsam:** Frida bağlantı sorunları, hook hataları, platform kaynaklı problemler  
> **Frida Sürümü:** 16.2.x  
> **Format:** Hata → Kök Neden → Çözüm

---

## Hızlı Tanı Komutu

```bash
# Ortamın durumunu tek komutla kontrol et
source .venv/bin/activate && frida --version && frida-ls-devices
```

---

## Kategori 1: Bağlantı & Oturum Hataları

### ❌ `RPCException: unable to handle message`

**Belirti:** Python tarafında `script.exports.init()` çağrısı sonrası `RPCException` fırlar.

**Kök Nedenler:**

1. JS tarafındaki `rpc.exports` objesi henüz yüklenmeden Python çağrı yapmaya çalışıyor.
2. `sentinel_loader.js` içinde syntax hatası var, script yüklenmedi.
3. Frida sürümü ile `frida-compile` çıktısı uyumsuz.

**Çözüm:**

```python
# ❌ Yanlış: script yüklenirken hemen çağrı
script = session.create_script(source)
script.load()
result = script.exports.init(config)  # Henüz hazır değil!

# ✅ Doğru: on_message callback ile hazırlık sinyali bekle
def on_message(message, data):
    if message['type'] == 'send' and message['payload'] == 'ready':
        script.exports.init(config)

script.on('message', on_message)
script.load()
```

---

### ❌ `PermissionDenied: unable to attach`

**Belirti:** `frida.attach(pid)` çağrısında izin hatası.

**Kök Nedenler:**

| Durum | Açıklama |
|:------|:---------|
| `frida-server` çalışmıyor | Cihazda `frida-server` başlatılmadı |
| Yanlış mimari | `arm64e` cihazda `arm64` binary kullanılıyor |
| SIP aktif (Mac host) | macOS System Integrity Protection Frida'yı engelliyor |
| USB bağlantı yok | `frida-ls-devices` listede cihazı göstermiyor |

**Çözüm:**

```bash
# 1. Cihazda frida-server'ı doğru başlat (jailbroken cihazda)
ssh root@<cihaz-ip>
/usr/sbin/frida-server &

# 2. Mimariyi doğrula
frida-ls-devices
# Çıktıda: iPhone (id: ...) görünmeli

# 3. Test bağlantısı
frida -U -n SpringBoard
# Başarılıysa REPL açılır
```

---

### ❌ `Failed to spawn: unable to find process with name`

**Belirti:** `frida.spawn()` veya `frida.attach()` uygulamayı bulamıyor.

**Çözüm:**

```bash
# Çalışan process listesini al
frida-ps -Ua   # USB bağlı cihaz, yüklü uygulamalar

# Doğru Bundle ID'yi bul
frida-ps -Uai | grep -i "banking"

# Bundle ID ile spawn
frida -U -f com.example.bankapp --no-pause
```

---

## Kategori 2: Hook Çalışma Hataları

### ❌ `TypeError: not a function` (ObjC method hook)

**Belirti:** `ObjC.classes.SomeClass['- methodName']` undefined veya çağrılamaz döner.

**Kök Nedenler:**

1. Method ismi yanlış — sınıf bu method'u implemente etmiyor.
2. Method lazy-load ediliyor; class henüz memory'de değil.
3. Swift obfuscation — method `_$S...` mangled isimle export edilmiş.

**Çözüm:**

```js
// 1. Sınıfın gerçekten o methodu içerip içermediğini kontrol et
const cls = ObjC.classes.LAContext;
console.log(cls.$ownMethods.join('\n'));  // Tüm methodları listele

// 2. Lazy class için ObjC.schedule kullan
ObjC.schedule(ObjC.mainQueue, function() {
  const target = ObjC.classes.LAContext['- evaluatePolicy:localizedReason:reply:'];
  if (target) Interceptor.attach(target.implementation, { ... });
});

// 3. Swift mangled isim için export tara
const mod = Process.getModuleByName('TargetApp');
mod.enumerateExports().filter(e => e.name.includes('evaluatePolicy'));
```

---

### ❌ `Error: access violation reading 0x...` (Native hook crash)

**Belirti:** `stat64` veya `access` hook'u uygulamayı çökertiyor.

**Kök Neden:** `onEnter` içinde `args[0].readUtf8String()` null pointer okumaya çalışıyor.

**Çözüm — Safe Boot wrapper:**

```js
// ❌ Yanlış: doğrudan okuma
onEnter(args) {
  this.path = args[0].readUtf8String();  // NULL ise crash!
}

// ✅ Doğru: null guard
onEnter(args) {
  try {
    this.path = args[0].isNull() ? '' : args[0].readUtf8String();
  } catch (e) {
    this.path = '';
    send({ type: 'warning', msg: 'stat64 null path', error: e.message });
  }
}
```

---

### ❌ `Error: Module 'Security' not found`

**Belirti:** `Module.findExportByName('Security', 'SecItemCopyMatching')` null döner.

**Çözüm:**

```js
// Framework adı değil, dylib yolunu kullan
const SEC = Module.findExportByName(
  '/System/Library/Frameworks/Security.framework/Security',
  'SecItemCopyMatching'
);

// Alternatif: tüm module'lerde tara
const sym = Process.findExportByName('SecItemCopyMatching');
```

---

## Kategori 3: Kamera / Frame Enjeksiyon Hataları

### ❌ `CVReturn error: -6680` (kCVReturnInvalidArgument)

**Belirti:** `CVPixelBufferCreate` hata kodu döndürüyor, sahte buffer oluşturuluyor.

**Kök Neden:** Pixel format veya boyut hedef uygulamanın beklentisiyle uyumsuz.

**Çözüm:**

```js
// Orijinal buffer'ın format ve boyutunu al, aynısıyla yeni buffer oluştur
const origBuf = CMSampleBufferGetImageBuffer(realSampleBuffer);
const width  = CVPixelBufferGetWidth(origBuf);
const height = CVPixelBufferGetHeight(origBuf);
const fmt    = CVPixelBufferGetPixelFormatType(origBuf);  // Genelde 875704438 = kCVPixelFormatType_420YpCbCr8BiPlanarFullRange

// Aynı parametrelerle sahte buffer oluştur
CVPixelBufferCreate(kCFAllocatorDefault, width, height, fmt, null, fakeBufferRef);
```

---

### ❌ Kamera Ekranı Donuyor / Siyah Görünüyor

**Belirti:** Frame enjeksiyonu sonrası uygulama kamera preview'unu donuk gösteriyor.

**Kök Neden:** `CMSampleBufferRef`'in `presentationTimeStamp` ve `duration` değerleri yanlış.

**Çözüm:**

```js
// Orijinal timestamp'i sahte buffer'a kopyala
const origTimestamp = CMSampleBufferGetPresentationTimeStamp(realSampleBuffer);
// Sahte buffer oluşturulurken bu timestamp kullanılmalı
CMSampleBufferCreateForImageBuffer(
  allocator, fakePixelBuffer,
  true, null, null,
  formatDescription,
  origTimestamp,  // ← Gerçek zamanı kullan
  origTimestamp,
  fakeBufferRef
);
```

---

## Kategori 4: Ortam & Kurulum Sorunları

### ❌ `frida-compile: command not found`

```bash
# npx ile çalıştır
npx frida-compile src/hooks/ios/cloak.js -o dist/cloak.js

# Yoksa yeniden kur
npm install --save-dev frida-compile
```

---

### ❌ `ImportError: No module named 'frida'`

```bash
# Sanal ortam aktif mi?
which python  # .venv/bin/python göstermeli

# Değilse aktifleştir
source .venv/bin/activate
pip install frida==16.2.1 frida-tools==16.2.1
```

---

### ❌ Frida port 27042 zaten kullanımda

```bash
# Eski frida-server process'ini öldür
pkill -9 frida-server
lsof -i :27042  # Kontrol et
```

---

## Genel Tanı Araçları

| Araç | Komut | Ne İşe Yarar |
|:-----|:------|:-------------|
| Cihaz listesi | `frida-ls-devices` | Bağlı cihazları gösterir |
| Process listesi | `frida-ps -Ua` | Uygulamaların PID & Bundle ID'si |
| Canlı REPL | `frida -U -n AppName` | Anlık JS çalıştırma |
| Trace mode | `frida-trace -U -n AppName -m "LAContext"` | Method çağrılarını otomatik logla |
| Objection | `objection -g AppName explore` | Yüksek seviyeli interaktif bypass |

---

*Bkz: [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`HOOK_REFERENCE.md`](HOOK_REFERENCE.md) · [`QUICKSTART.md`](QUICKSTART.md)*
