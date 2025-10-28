from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import login_required, current_user
from models import db, Truck, Driver, Shipment, Revenue, Expense, MaintenanceRecord, Notification, Report, User
from advanced_routes import advanced_bp
from auth import init_auth
from driver_account import calculate_driver_account, get_driver_account_details, get_all_drivers_accounts, get_drivers_summary
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

# إعدادات قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trucks_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_ARABIC_SUPPORT'] = True
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'  # يجب تغييره في الإنتاج

# تفعيل CORS
CORS(app)

# تهيئة قاعدة البيانات
db.init_app(app)

# تهيئة نظام المصادقة
init_auth(app)

# تسجيل Blueprint للمسارات المتقدمة
app.register_blueprint(advanced_bp)

# إنشاء جداول قاعدة البيانات
with app.app_context():
    db.create_all()

# ============ API Routes - القواطر ============

@app.route('/api/trucks', methods=['GET'])
@login_required
def get_trucks():
    """الحصول على قائمة القواطر"""
    trucks = Truck.query.all()
    return jsonify([truck.to_dict() for truck in trucks])

@app.route('/api/trucks/<int:truck_id>', methods=['GET'])
@login_required
def get_truck(truck_id):
    """الحصول على بيانات قاطرة محددة"""
    truck = Truck.query.get_or_404(truck_id)
    return jsonify(truck.to_dict())

@app.route('/api/trucks', methods=['POST'])
@login_required
def create_truck():
    """إضافة قاطرة جديدة"""
    data = request.get_json()
    truck = Truck(
        truck_type=data.get('truck_type'),
        plate_number=data.get('plate_number'),
        status=data.get('status', 'active')
    )
    db.session.add(truck)
    db.session.commit()
    return jsonify(truck.to_dict()), 201

@app.route('/api/trucks/<int:truck_id>', methods=['PUT'])
@login_required
def update_truck(truck_id):
    """تحديث بيانات قاطرة"""
    truck = Truck.query.get_or_404(truck_id)
    data = request.get_json()
    
    if 'truck_type' in data:
        truck.truck_type = data['truck_type']
    if 'plate_number' in data:
        truck.plate_number = data['plate_number']
    if 'status' in data:
        truck.status = data['status']
    if 'last_maintenance_date' in data and data['last_maintenance_date']:
        try:
            truck.last_maintenance_date = datetime.fromisoformat(data['last_maintenance_date'])
        except ValueError:
            pass
    
    db.session.commit()
    return jsonify(truck.to_dict())

@app.route('/api/trucks/<int:truck_id>', methods=['DELETE'])
@login_required
def delete_truck(truck_id):
    """حذف قاطرة"""
    truck = Truck.query.get_or_404(truck_id)
    db.session.delete(truck)
    db.session.commit()
    return '', 204

# ============ API Routes - السائقين ============

@app.route('/api/drivers', methods=['GET'])
@login_required
def get_drivers():
    """الحصول على قائمة السائقين"""
    drivers = Driver.query.all()
    return jsonify([driver.to_dict() for driver in drivers])

@app.route('/api/drivers', methods=['POST'])
@login_required
def create_driver():
    """إضافة سائق جديد"""
    data = request.get_json()
    driver = Driver(
        name=data.get('name'),
        phone_number=data.get('phone_number'),
        salary=data.get('salary'),
        truck_id=data.get('truck_id'),
        status=data.get('status', 'active')
    )
    db.session.add(driver)
    db.session.commit()
    return jsonify(driver.to_dict()), 201

@app.route('/api/drivers/<int:driver_id>', methods=['PUT'])
@login_required
def update_driver(driver_id):
    """تحديث بيانات سائق"""
    driver = Driver.query.get_or_404(driver_id)
    data = request.get_json()
    
    if 'name' in data:
        driver.name = data['name']
    if 'phone_number' in data:
        driver.phone_number = data['phone_number']
    if 'salary' in data:
        driver.salary = data['salary']
    if 'truck_id' in data:
        driver.truck_id = data['truck_id']
    if 'status' in data:
        driver.status = data['status']
    
    db.session.commit()
    return jsonify(driver.to_dict())

@app.route('/api/drivers/<int:driver_id>', methods=['DELETE'])
@login_required
def delete_driver(driver_id):
    """حذف سائق"""
    driver = Driver.query.get_or_404(driver_id)
    db.session.delete(driver)
    db.session.commit()
    return '', 204

# ============ API Routes - الشحنات ============

@app.route('/api/shipments', methods=['GET'])
@login_required
def get_shipments():
    """الحصول على قائمة الشحنات"""
    shipments = Shipment.query.all()
    return jsonify([shipment.to_dict() for shipment in shipments])

@app.route('/api/shipments', methods=['POST'])
@login_required
def create_shipment():
    """إضافة شحنة جديدة"""
    data = request.get_json()
    shipment = Shipment(
        truck_id=data.get('truck_id'),
        driver_id=data.get('driver_id'),
        from_location=data.get('from_location'),
        to_location=data.get('to_location'),
        cargo=data.get('cargo'),
        revenue=data.get('revenue'),
        status=data.get('status', 'pending')
    )
    db.session.add(shipment)
    
    truck = Truck.query.get(data.get('truck_id'))
    if truck:
        truck.total_shipments += 1
    
    db.session.commit()
    return jsonify(shipment.to_dict()), 201

@app.route('/api/shipments/<int:shipment_id>', methods=['PUT'])
@login_required
def update_shipment(shipment_id):
    """تحديث حالة الشحنة"""
    shipment = Shipment.query.get_or_404(shipment_id)
    data = request.get_json()
    
    if 'status' in data:
        shipment.status = data['status']
    if 'revenue' in data:
        shipment.revenue = data['revenue']
    
    db.session.commit()
    return jsonify(shipment.to_dict())

# ============ API Routes - الإيرادات والمصاريف ============

@app.route('/api/revenues', methods=['GET'])
@login_required
def get_revenues():
    """الحصول على قائمة الإيرادات"""
    revenues = Revenue.query.all()
    return jsonify([revenue.to_dict() for revenue in revenues])

@app.route('/api/revenues', methods=['POST'])
@login_required
def create_revenue():
    """إضافة إيراد جديد"""
    data = request.get_json()
    revenue = Revenue(
        truck_id=data.get('truck_id'),
        shipment_id=data.get('shipment_id'),
        amount=data.get('amount'),
        description=data.get('description')
    )
    db.session.add(revenue)
    db.session.commit()
    return jsonify(revenue.to_dict()), 201

@app.route('/api/expenses', methods=['GET'])
@login_required
def get_expenses():
    """الحصول على قائمة المصاريف"""
    expenses = Expense.query.all()
    return jsonify([expense.to_dict() for expense in expenses])

@app.route('/api/expenses', methods=['POST'])
@login_required
def create_expense():
    """إضافة مصروف جديد"""
    data = request.get_json()
    expense = Expense(
        truck_id=data.get('truck_id'),
        driver_id=data.get('driver_id'),
        expense_type=data.get('expense_type'),
        amount=data.get('amount'),
        description=data.get('description')
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201

# ============ API Routes - الصيانة ============

@app.route('/api/maintenance', methods=['GET'])
@login_required
def get_maintenance():
    """الحصول على سجل الصيانة"""
    records = MaintenanceRecord.query.all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/maintenance', methods=['POST'])
@login_required
def create_maintenance():
    """إضافة سجل صيانة جديد"""
    data = request.get_json()
    record = MaintenanceRecord(
        truck_id=data.get('truck_id'),
        maintenance_type=data.get('maintenance_type'),
        cost=data.get('cost'),
        description=data.get('description')
    )
    db.session.add(record)
    
    truck = Truck.query.get(data.get('truck_id'))
    if truck:
        truck.last_maintenance_date = datetime.utcnow()
        expense = Expense(
            truck_id=data.get('truck_id'),
            driver_id=None,
            expense_type='maintenance',
            amount=data.get('cost'),
            description=f"صيانة: {data.get('maintenance_type')} - {data.get('description')}"
        )
        db.session.add(expense)
    
    db.session.commit()
    return jsonify(record.to_dict()), 201

# ============ API Routes - التحليلات والتقارير ============

@app.route('/api/analytics/truck-profit/<int:truck_id>', methods=['GET'])
@login_required
def get_truck_profit(truck_id):
    """حساب ربح/خسارة قاطرة محددة"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    else:
        start_date = datetime.utcnow() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    else:
        end_date = datetime.utcnow()
    
    revenues = db.session.query(db.func.sum(Revenue.amount)).filter(
        Revenue.truck_id == truck_id,
        Revenue.revenue_date >= start_date,
        Revenue.revenue_date <= end_date
    ).scalar() or 0
    
    expenses = db.session.query(db.func.sum(Expense.amount)).filter(
        Expense.truck_id == truck_id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).scalar() or 0
    
    profit = revenues - expenses
    
    return jsonify({
        'truck_id': truck_id,
        'revenue': float(revenues),
        'expenses': float(expenses),
        'profit': float(profit),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    })

@app.route('/api/analytics/fleet-summary', methods=['GET'])
@login_required
def get_fleet_summary():
    """ملخص الأسطول"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    else:
        start_date = datetime.utcnow() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    else:
        end_date = datetime.utcnow()
    
    trucks = Truck.query.all()
    trucks_data = []
    total_revenue = 0
    total_expenses = 0
    
    for truck in trucks:
        revenue = db.session.query(db.func.sum(Revenue.amount)).filter(
            Revenue.truck_id == truck.id,
            Revenue.revenue_date >= start_date,
            Revenue.revenue_date <= end_date
        ).scalar() or 0
        
        expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.truck_id == truck.id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).scalar() or 0
        
        profit = revenue - expenses
        total_revenue += revenue
        total_expenses += expenses
        
        trucks_data.append({
            'truck': truck.to_dict(),
            'revenue': float(revenue),
            'expenses': float(expenses),
            'profit': float(profit)
        })
    
    return jsonify({
        'trucks': trucks_data,
        'total_revenue': float(total_revenue),
        'total_expenses': float(total_expenses),
        'total_profit': float(total_revenue - total_expenses),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    })

# ============ API Routes - الإشعارات ============

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_all_notifications():
    """الحصول على جميع الإشعارات"""
    limit = request.args.get('limit', 50, type=int)
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(limit).all()
    return jsonify([notification.to_dict() for notification in notifications])

@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """حذف إشعار"""
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    return '', 204

@app.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    """الحصول على بيانات لوحة التحكم"""
    trucks = Truck.query.all()
    drivers = Driver.query.all()
    shipments = Shipment.query.all()
    
    active_trucks = len([t for t in trucks if t.status == 'active'])
    maintenance_trucks = len([t for t in trucks if t.status == 'maintenance'])
    
    pending_shipments = len([s for s in shipments if s.status == 'pending'])
    in_transit = len([s for s in shipments if s.status == 'in_transit'])
    delivered = len([s for s in shipments if s.status == 'delivered'])
    
    start_date = datetime.utcnow() - timedelta(days=30)
    total_revenue = db.session.query(db.func.sum(Revenue.amount)).filter(
        Revenue.revenue_date >= start_date
    ).scalar() or 0
    
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
        Expense.expense_date >= start_date
    ).scalar() or 0
    
    return jsonify({
        'trucks': {
            'total': len(trucks),
            'active': active_trucks,
            'maintenance': maintenance_trucks,
            'stopped': len(trucks) - active_trucks - maintenance_trucks
        },
        'drivers': {
            'total': len(drivers),
            'active': len([d for d in drivers if d.status == 'active'])
        },
        'shipments': {
            'total': len(shipments),
            'pending': pending_shipments,
            'in_transit': in_transit,
            'delivered': delivered
        },
        'financials': {
            'revenue': float(total_revenue),
            'expenses': float(total_expenses),
            'profit': float(total_revenue - total_expenses)
        }
    })

# ============ API Routes - كشف حساب السائق ============

@app.route('/api/drivers/<int:driver_id>/account', methods=['GET'])
@login_required
def get_driver_account(driver_id):
    """الحصول على كشف حساب السائق"""
    account = calculate_driver_account(driver_id)
    if not account:
        return jsonify({'error': 'السائق غير موجود'}), 404
    return jsonify(account)

@app.route('/api/drivers/<int:driver_id>/account-details', methods=['GET'])
@login_required
def get_driver_account_full(driver_id):
    """الحصول على تفاصيل كاملة لكشف حساب السائق"""
    details = get_driver_account_details(driver_id)
    if not details:
        return jsonify({'error': 'السائق غير موجود'}), 404
    return jsonify(details)

@app.route('/api/drivers/accounts/all', methods=['GET'])
@login_required
def get_all_drivers_accounts_api():
    """الحصول على كشف حساب جميع السائقين"""
    accounts = get_all_drivers_accounts()
    return jsonify(accounts)

@app.route('/api/drivers/accounts/summary', methods=['GET'])
@login_required
def get_drivers_summary_api():
    """الحصول على ملخص إحصائي لجميع السائقين"""
    summary = get_drivers_summary()
    return jsonify(summary)

# ============ صفحات HTML ============

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """صفحة تسجيل الدخول"""
    return render_template('login.html')

@app.route('/users')
@login_required
def users_page():
    """صفحة إدارة المستخدمين"""
    if current_user.role != 'admin':
        return render_template('unauthorized.html'), 403
    return render_template('users.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم"""
    return render_template('dashboard.html')

@app.route('/trucks')
@login_required
def trucks_page():
    """صفحة إدارة القواطر"""
    return render_template('trucks.html')

@app.route('/drivers')
@login_required
def drivers_page():
    """صفحة إدارة السائقين"""
    return render_template('drivers.html')

@app.route('/shipments')
@login_required
def shipments_page():
    """صفحة إدارة الشحنات"""
    return render_template('shipments.html')

@app.route('/reports')
@login_required
def reports_page():
    """صفحة التقارير"""
    return render_template('reports.html')

@app.route('/expenses')
@login_required
def expenses_page():
    """صفحة إدارة المصاريف"""
    return render_template('expenses.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
