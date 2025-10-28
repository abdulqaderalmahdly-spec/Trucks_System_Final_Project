"""
نظام المصادقة والتحقق من المستخدمين
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
login_manager = LoginManager()

def init_auth(app):
    """تهيئة نظام المصادقة"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول أولاً'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.register_blueprint(auth_bp)
    
    # إنشاء المستخدم الافتراضي (admin)
    with app.app_context():
        create_default_admin()


def create_default_admin():
    """إنشاء مستخدم admin افتراضي إذا لم يكن موجوداً"""
    admin_user = User.query.filter_by(username='admin').first()
    
    if not admin_user:
        admin = User(
            username='admin',
            email='admin@trucks-system.com',
            full_name='مدير النظام',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')  # كلمة المرور الافتراضية
        db.session.add(admin)
        db.session.commit()
        print("✓ تم إنشاء المستخدم الافتراضي (admin) بنجاح")
        print("  اسم المستخدم: admin")
        print("  كلمة المرور: admin123")
    else:
        print("✓ المستخدم الافتراضي (admin) موجود بالفعل")


# ============ مسارات المصادقة ============

@auth_bp.route('/login', methods=['POST'])
def login():
    """تسجيل الدخول"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'حساب المستخدم غير مفعل'}), 403
    
    # تحديث آخر وقت تسجيل دخول
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # تسجيل الدخول
    login_user(user, remember=True)
    
    return jsonify({
        'message': 'تم تسجيل الدخول بنجاح',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    return jsonify({'message': 'تم تسجيل الخروج بنجاح'}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """تسجيل مستخدم جديد"""
    data = request.get_json()
    
    # التحقق من البيانات المطلوبة
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'اسم المستخدم والبريد الإلكتروني وكلمة المرور مطلوبة'}), 400
    
    # التحقق من عدم وجود المستخدم بالفعل
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'اسم المستخدم موجود بالفعل'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'البريد الإلكتروني مسجل بالفعل'}), 409
    
    # إنشاء مستخدم جديد
    new_user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name', ''),
        role='user'  # الدور الافتراضي للمستخدمين الجدد
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء الحساب بنجاح',
        'user': new_user.to_dict()
    }), 201


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """الحصول على بيانات المستخدم الحالي"""
    return jsonify(current_user.to_dict()), 200


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """تغيير كلمة المرور"""
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'كلمة المرور القديمة والجديدة مطلوبة'}), 400
    
    # التحقق من كلمة المرور القديمة
    if not current_user.check_password(data['old_password']):
        return jsonify({'error': 'كلمة المرور القديمة غير صحيحة'}), 401
    
    # تحديث كلمة المرور
    current_user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'تم تغيير كلمة المرور بنجاح'}), 200


@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """التحقق من حالة جلسة المستخدم"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        }), 200
    else:
        return jsonify({'authenticated': False}), 200


# ============ مسارات إدارة المستخدمين (للمسؤولين فقط) ============

@auth_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """الحصول على قائمة جميع المستخدمين (للمسؤولين فقط)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'ليس لديك صلاحيات كافية'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """الحصول على بيانات مستخدم محدد"""
    if current_user.role != 'admin' and current_user.id != user_id:
        return jsonify({'error': 'ليس لديك صلاحيات كافية'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """تحديث بيانات مستخدم"""
    if current_user.role != 'admin' and current_user.id != user_id:
        return jsonify({'error': 'ليس لديك صلاحيات كافية'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # تحديث البيانات المسموحة
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    if 'email' in data:
        # التحقق من عدم وجود بريد إلكتروني مكرر
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'البريد الإلكتروني مسجل بالفعل'}), 409
        user.email = data['email']
    
    # فقط المسؤول يمكنه تغيير الدور والحالة
    if current_user.role == 'admin':
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': 'تم تحديث البيانات بنجاح',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """حذف مستخدم (للمسؤولين فقط)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'ليس لديك صلاحيات كافية'}), 403
    
    if user_id == current_user.id:
        return jsonify({'error': 'لا يمكنك حذف حسابك الخاص'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'تم حذف المستخدم بنجاح'}), 200


@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """تفعيل/تعطيل حساب مستخدم (للمسؤولين فقط)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'ليس لديك صلاحيات كافية'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'مفعل' if user.is_active else 'معطل'
    return jsonify({
        'message': f'تم {status} حساب المستخدم بنجاح',
        'user': user.to_dict()
    }), 200
