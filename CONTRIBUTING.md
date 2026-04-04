<div align="center">

# 🤝 CONTRIBUTING

### Sentinel Hook'a Katkıda Bulunmak

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge&logo=github)](https://github.com/Kadiraricii/Sentinel_Hook/pulls)
[![Contributions](https://img.shields.io/badge/Contributions-Open-00C9FF?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](https://github.com/Kadiraricii/Sentinel_Hook/issues)

</div>

---

## 📋 Başlamadan Önce

> [!IMPORTANT]
> Katkıda bulunmadan önce `DISCLAIMER.md` dosyasını okuyun ve etik kurallara uymayı taahhüt edin.

1. Katkınızın mevcut bir `Issue` ile örtüşüp örtüşmediğini kontrol edin.
2. Yoksa yeni bir Issue açın ve onaylandıktan sonra geliştirmeye başlayın.

---

## 🔀 Branch Stratejisi

```
main              →  Stabil, production-ready branch
dev               →  Aktif geliştirme (PR'lar buraya açılır)
feature/<isim>    →  Yeni özellik geliştirme
fix/<isim>        →  Bug / Hata düzeltmeleri
```

```bash
# 1. Fork'la ve klonla
git clone https://github.com/<siz>/Sentinel_Hook.git
cd Sentinel_Hook

# 2. Yeni branch oluştur
git checkout -b feature/yeni-bypass-modulu

# 3. Geliştir ve commit'le
git add .
git commit -m "feat(hooks): android SafetyNet bypass eklendi"

# 4. Push et ve PR aç
git push origin feature/yeni-bypass-modulu
```

---

## 📝 Commit Mesajı Formatı

Projede [Conventional Commits](https://www.conventionalcommits.org/) standardı kullanılır:

| Tip | Kullanım |
|:----|:---------|
| `feat` | Yeni özellik |
| `fix` | Hata düzeltmesi |
| `docs` | Dokümantasyon değişikliği |
| `refactor` | Yeniden yapılandırma |
| `test` | Test ekleme / güncelleme |
| `chore` | Bağımlılık / build güncellemeleri |

**Örnekler:**
```
feat(ios): VNFaceObservation sahte inject eklendi
fix(android): TrustManager null pointer hatası giderildi
docs(readme): kurulum adımları güncellendi
```

---

## 🧪 Kalite Standartları

> [!TIP]
> Her yeni bypass modülü için aşağıdaki kriterleri karşıladığından emin ol.

- **JS Hook'ları:** Her script `console.log` ile aktif olduğunu bildirmeli ve `try/catch` ile çalışmalıdır.
- **Swift/Java:** Hook atacağın metotlar `@objc dynamic` veya `public` olmalıdır.
- **Test:** Yeni bir bypass ekleniyorsa `DummyBank` üzerinde test edilmeli ve PR açıklamasına terminal çıktısı eklenmelidir.

---

## 🚫 Kabul Edilmeyen Katkılar

> [!CAUTION]
> Aşağıdaki türdeki PR'lar doğrudan kapatılır:

- Gerçek banka/fintech uygulamalarını hedef alan spesifik exploit kodları
- Kullanıcı verisi toplayan herhangi bir modül
- Lisans ve etik sorumluluk reddi metinlerini kaldıran değişiklikler
