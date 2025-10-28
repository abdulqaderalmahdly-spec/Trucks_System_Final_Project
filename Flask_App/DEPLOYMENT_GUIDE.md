# دليل نشر نظام إدارة القواطر

هذا الدليل يشرح كيفية نشر تطبيق **Trucks_system** على خوادم ويب دائمة.

## الخيار 1: النشر على Render (مجاني وسهل)

### الخطوات:

1. **إنشاء حساب على Render:**
   - اذهب إلى [render.com](https://render.com)
   - قم بإنشاء حساب جديد (يمكنك استخدام حسابك على GitHub)

2. **ربط مستودع GitHub:**
   - ادفع ملفات المشروع إلى مستودع GitHub خاص بك
   - في Render، اختر "New +" ثم "Web Service"
   - اختر "Connect a repository"
   - اختر المستودع الذي يحتوي على ملفات المشروع

3. **تكوين الإعدادات:**
   - **Name:** `trucks-system` (أو أي اسم تفضله)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** اختر "Free" للخطة المجانية

4. **إضافة متغيرات البيئة:**
   - انقر على "Environment"
   - أضف المتغيرات التالية:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-very-secret-key-here-change-this
     ```

5. **النشر:**
   - انقر على "Deploy"
   - انتظر حتى ينتهي النشر (قد يستغرق 5-10 دقائق)
   - ستحصل على رابط دائم مثل: `https://trucks-system.onrender.com`

---

## الخيار 2: النشر على Railway (سهل جداً)

### الخطوات:

1. **إنشاء حساب على Railway:**
   - اذهب إلى [railway.app](https://railway.app)
   - قم بإنشاء حساب جديد (يمكنك استخدام حسابك على GitHub)

2. **ربط مستودع GitHub:**
   - في Railway، انقر على "New Project"
   - اختر "Deploy from GitHub repo"
   - اختر المستودع الذي يحتوي على ملفات المشروع

3. **تكوين الإعدادات:**
   - Railway سيكتشف تلقائياً أنه مشروع Python
   - سيقرأ `requirements.txt` و `Procfile` تلقائياً

4. **إضافة متغيرات البيئة:**
   - انقر على "Variables"
   - أضف المتغيرات التالية:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-very-secret-key-here-change-this
     ```

5. **النشر:**
   - Railway سينشر التطبيق تلقائياً
   - ستحصل على رابط دائم مثل: `https://trucks-system-production.up.railway.app`

---

## الخيار 3: النشر على Heroku (مدفوع، لكن موثوق)

### الخطوات:

1. **تثبيت Heroku CLI:**
   ```bash
   # على Windows
   choco install heroku-cli
   
   # على Mac
   brew tap heroku/brew && brew install heroku
   
   # على Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **تسجيل الدخول:**
   ```bash
   heroku login
   ```

3. **إنشاء تطبيق جديد:**
   ```bash
   heroku create trucks-system
   ```

4. **إضافة متغيرات البيئة:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-very-secret-key-here-change-this
   ```

5. **النشر:**
   ```bash
   git push heroku main
   ```

6. **الحصول على الرابط:**
   ```bash
   heroku open
   ```

---

## ملاحظات مهمة:

### 1. تغيير المفتاح السري (SECRET_KEY)
**لا تستخدم المفتاح الافتراضي في الإنتاج!** قم بتوليد مفتاح جديد:

```python
import secrets
print(secrets.token_hex(32))
```

### 2. قاعدة البيانات
في الإنتاج، يفضل استخدام قاعدة بيانات حقيقية بدلاً من SQLite:
- **PostgreSQL** (موصى به)
- **MySQL**

تحديث `app.py`:
```python
import os
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trucks_system.db'
```

### 3. الرابط الدائم
بعد النشر، ستحصل على رابط دائم مثل:
- **Render:** `https://trucks-system.onrender.com`
- **Railway:** `https://trucks-system-production.up.railway.app`
- **Heroku:** `https://trucks-system.herokuapp.com`

استخدم هذا الرابط في تطبيق Android WebView.

---

## اختبار التطبيق بعد النشر:

1. افتح الرابط الدائم في المتصفح
2. سجل الدخول باستخدام:
   - **اسم المستخدم:** `admin`
   - **كلمة المرور:** `admin123`

---

## استكشاف الأخطاء:

### إذا رأيت رسالة خطأ "Application failed to start":
```bash
# على Render
# انقر على "Logs" لرؤية رسائل الخطأ

# على Railway
# انقر على "Logs" لرؤية رسائل الخطأ

# على Heroku
heroku logs --tail
```

### إذا كانت قاعدة البيانات فارغة:
قد تحتاج إلى تشغيل أوامر إنشاء الجداول:
```python
# في ملف منفصل أو في shell
from app import app, db
with app.app_context():
    db.create_all()
```

---

## الخطوة التالية:

بعد النشر بنجاح، استخدم الرابط الدائم في تطبيق Android WebView.

تم إعداد هذا الدليل بواسطة **Manus AI**.
