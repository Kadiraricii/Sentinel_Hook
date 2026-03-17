# 🔒 Güvenlik Politikası (SECURITY POLICY)

## Desteklenen Sürümler

| Versiyon | Destek Durumu |
| :------- | :------------ |
| 1.0.x    | ✅ Aktif destek |
| < 1.0    | ❌ Destek yok  |

---

## 🐛 Güvenlik Açığı Bildirme

Sentinel Hook'un **kendi altyapısında** bir güvenlik açığı keşfettiyseniz (örneğin: scriptin hedeflenmeyen sistemlere erişim sağlaması, Python katmanında RCE riski vb.), lütfen bunu herkese açık bir Issue olarak paylaşmayın.

Bunun yerine:
1. Açığı detaylıca belgeleyin (PoC kodu varsa ekleyin)
2. `security@sentinel-hook.local` adresine (veya GitHub Private Vulnerability Reporting üzerinden) gönderin
3. 72 saat içinde yanıt alacaksınız

**Responsible Disclosure** ilkesine uygun hareket ettiğiniz için şimdiden teşekkür ederiz.

---

## ⚠️ Kapsam Dışı Konular

Aşağıdakiler bu güvenlik politikasının kapsamı **dışındadır:**
- Projede kasıtlı olarak tasarlanan bypass mekanizmalarının "açık" olarak raporlanması  
  *(Bunlar projenin amacıdır, hata değil)*
- Üçüncü taraf kütüphanelerin (Frida, mitmproxy) kendi açıkları
