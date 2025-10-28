from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """نموذج المستخدم مع تشفير كلمات المرور"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """تشفير كلمة المرور باستخدام Bcrypt"""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Truck(db.Model):
    __tablename__ = 'trucks'
    
    id = db.Column(db.Integer, primary_key=True)
    truck_type = db.Column(db.String(100), nullable=False)
    plate_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, maintenance, stopped
    last_maintenance_date = db.Column(db.DateTime)
    total_shipments = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    drivers = db.relationship('Driver', backref='truck', lazy=True, cascade='all, delete-orphan')
    shipments = db.relationship('Shipment', backref='truck', lazy=True, cascade='all, delete-orphan')
    revenues = db.relationship('Revenue', backref='truck', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='truck', lazy=True, cascade='all, delete-orphan')
    maintenance_records = db.relationship('MaintenanceRecord', backref='truck', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'truck_type': self.truck_type,
            'plate_number': self.plate_number,
            'status': self.status,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'total_shipments': self.total_shipments,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'))
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    shipments = db.relationship('Shipment', backref='driver', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='driver', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'salary': self.salary,
            'truck_id': self.truck_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Shipment(db.Model):
    __tablename__ = 'shipments'
    
    id = db.Column(db.Integer, primary_key=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    from_location = db.Column(db.String(255), nullable=False)
    to_location = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.Text, nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_transit, delivered
    shipment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    revenues = db.relationship('Revenue', backref='shipment', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'truck_id': self.truck_id,
            'driver_id': self.driver_id,
            'from_location': self.from_location,
            'to_location': self.to_location,
            'cargo': self.cargo,
            'revenue': self.revenue,
            'status': self.status,
            'shipment_date': self.shipment_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Revenue(db.Model):
    __tablename__ = 'revenues'
    
    id = db.Column(db.Integer, primary_key=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'), nullable=False)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'))
    amount = db.Column(db.Float, nullable=False)
    revenue_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'truck_id': self.truck_id,
            'shipment_id': self.shipment_id,
            'amount': self.amount,
            'revenue_date': self.revenue_date.isoformat(),
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    expense_type = db.Column(db.String(50), nullable=False)  # salary, maintenance, fuel, fine, other
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'truck_id': self.truck_id,
            'driver_id': self.driver_id,
            'expense_type': self.expense_type,
            'amount': self.amount,
            'expense_date': self.expense_date.isoformat(),
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'), nullable=False)
    maintenance_type = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    maintenance_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'truck_id': self.truck_id,
            'maintenance_type': self.maintenance_type,
            'cost': self.cost,
            'maintenance_date': self.maintenance_date.isoformat(),
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'))
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # maintenance, loss, performance, info
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'truck_id': self.truck_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # truck_profit, fleet_summary, expense_analysis, driver_performance
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_revenue = db.Column(db.Float, default=0)
    total_expenses = db.Column(db.Float, default=0)
    profit = db.Column(db.Float, default=0)
    report_data = db.Column(db.Text)  # JSON data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_type': self.report_type,
            'truck_id': self.truck_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'total_revenue': self.total_revenue,
            'total_expenses': self.total_expenses,
            'profit': self.profit,
            'report_data': self.report_data,
            'created_at': self.created_at.isoformat()
        }
