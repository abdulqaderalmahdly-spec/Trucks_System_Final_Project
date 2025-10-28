# تطبيق Trucks System - Android (WebView)

تطبيق Android بسيط يعتمد على **WebView** للوصول إلى نظام إدارة القواطر المتكامل.

## المتطلبات

- **Android Studio** (آخر إصدار)
- **JDK 8** أو أحدث
- **Android SDK** (API Level 21 أو أحدث)

## الخطوات للبناء والتشغيل

### 1. فتح المشروع في Android Studio

```bash
# انسخ مجلد TrucksSystemAndroid
# افتح Android Studio
# اختر File > Open
# اختر مجلد TrucksSystemAndroid
```

### 2. تحديث رابط التطبيق

قبل البناء، تأكد من تحديث رابط التطبيق الدائم في ملف `MainActivity.java`:

```java
private static final String APP_URL = "https://trucks-system.onrender.com/login";
```

استبدل الرابط بالرابط الدائم الخاص بتطبيقك (بعد نشره على Render أو Railway).

### 3. بناء التطبيق

```bash
# في Android Studio:
# Build > Build Bundle(s) / APK(s) > Build APK(s)
```

### 4. تشغيل التطبيق

```bash
# في Android Studio:
# Run > Run 'app'
# اختر جهاز أو محاكي
```

## بناء ملف APK للتوزيع

### الخطوة 1: إنشاء مفتاح التوقيع (Signing Key)

```bash
# في Android Studio:
# Build > Generate Signed Bundle / APK
# اختر APK
# اضغط Next
# اختر "Create new..."
# ملء البيانات المطلوبة
```

### الخطوة 2: بناء APK موقع

```bash
# اتبع الخطوات السابقة
# اختر Release
# اضغط Finish
```

سيتم حفظ ملف APK في:
```
app/release/app-release.apk
```

## توزيع التطبيق

يمكنك توزيع ملف APK بالطرق التالية:

1. **Google Play Store** - تحميل التطبيق على متجر جوجل
2. **توزيع مباشر** - إرسال ملف APK للمستخدمين
3. **Firebase App Distribution** - توزيع الإصدارات التجريبية

## ملاحظات مهمة

### 1. تحديث الرابط الدائم

عند نشر تطبيق Flask على Render أو Railway، ستحصل على رابط دائم مثل:
- `https://trucks-system.onrender.com`
- `https://trucks-system-production.up.railway.app`

**تأكد من تحديث هذا الرابط في `MainActivity.java` قبل بناء APK.**

### 2. الأذونات

التطبيق يتطلب الأذونات التالية (مضافة بالفعل في `AndroidManifest.xml`):
- `INTERNET` - للوصول إلى الإنترنت
- `ACCESS_NETWORK_STATE` - للتحقق من حالة الاتصال

### 3. الأمان

- **استخدم HTTPS فقط** - تأكد من أن الرابط الدائم يستخدم HTTPS
- **تحديث المفتاح السري** - غير المفتاح السري في Flask قبل النشر
- **توقيع التطبيق** - استخدم مفتاح توقيع قوي عند بناء APK

## استكشاف الأخطاء

### الخطأ: "Unable to connect to server"

- تأكد من أن الرابط الدائم صحيح
- تأكد من أن الخادم يعمل
- تحقق من اتصال الإنترنت

### الخطأ: "SSL Certificate Error"

- تأكد من استخدام HTTPS
- تحقق من صحة شهادة SSL على الخادم

### الخطأ: "WebView not loading"

- تأكد من تفعيل JavaScript في WebSettings
- تحقق من سجلات Android Studio (Logcat)

## الملفات الرئيسية

| الملف | الوصف |
|------|--------|
| `MainActivity.java` | النشاط الرئيسي الذي يحتوي على WebView |
| `activity_main.xml` | تخطيط واجهة المستخدم |
| `AndroidManifest.xml` | ملف إعدادات التطبيق |
| `build.gradle` | إعدادات البناء والمكتبات |

## الدعم والمساعدة

للمزيد من المعلومات عن بناء تطبيقات Android، راجع:
- [Android Developer Documentation](https://developer.android.com)
- [WebView Documentation](https://developer.android.com/reference/android/webkit/WebView)

---

تم إعداد هذا التطبيق بواسطة **Manus AI**.
