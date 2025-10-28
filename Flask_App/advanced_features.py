"""
ميزات متقدمة لنظام إدارة القواطر
- نظام الإشعارات الذكية
- التحليلات المتقدمة
- التنبيهات التلقائية
"""

from models import db, Truck, Driver, Shipment, Revenue, Expense, MaintenanceRecord, Notification
from datetime import datetime, timedelta
from flask import jsonify

class NotificationSystem:
    """نظام الإشعارات الذكية"""
    
    @staticmethod
    def check_maintenance_due(truck_id, days_threshold=30):
        """التحقق من الصيانة المستحقة"""
        truck = Truck.query.get(truck_id)
        if not truck:
            return False
        
        if truck.last_maintenance_date is None:
            return True
        
        days_since_maintenance = (datetime.utcnow() - truck.last_maintenance_date).days
        
        if days_since_maintenance >= days_threshold:
            # إنشاء إشعار
            notification = Notification(
                truck_id=truck_id,
                title=f"صيانة مستحقة للقاطرة {truck.plate_number}",
                message=f"آخر صيانة كانت قبل {days_since_maintenance} يوم. يرجى جدولة الصيانة",
                notification_type='maintenance',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def check_truck_profitability(truck_id, days=30):
        """التحقق من ربحية القاطرة"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # حساب الإيرادات
        revenues = db.session.query(db.func.sum(Revenue.amount)).filter(
            Revenue.truck_id == truck_id,
            Revenue.revenue_date >= start_date
        ).scalar() or 0
        
        # حساب المصاريف
        expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.truck_id == truck_id,
            Expense.expense_date >= start_date
        ).scalar() or 0
        
        profit = revenues - expenses
        
        if profit < 0:
            truck = Truck.query.get(truck_id)
            notification = Notification(
                truck_id=truck_id,
                title=f"تحذير: خسارة للقاطرة {truck.plate_number}",
                message=f"القاطرة تسجل خسارة بمقدار {abs(profit):.2f} في آخر {days} يوم",
                notification_type='loss',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            return False
        
        return True
    
    @staticmethod
    def get_unread_notifications():
        """الحصول على الإشعارات غير المقروءة"""
        notifications = Notification.query.filter_by(is_read=False).all()
        return [notification.to_dict() for notification in notifications]
    
    @staticmethod
    def mark_notification_as_read(notification_id):
        """تحديد الإشعار كمقروء"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False


class AdvancedAnalytics:
    """التحليلات المتقدمة للنظام"""
    
    @staticmethod
    def get_truck_performance_metrics(truck_id, days=30):
        """حساب مقاييس أداء القاطرة"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # عدد الشحنات
        shipments = Shipment.query.filter(
            Shipment.truck_id == truck_id,
            Shipment.shipment_date >= start_date
        ).all()
        
        total_shipments = len(shipments)
        delivered_shipments = len([s for s in shipments if s.status == 'delivered'])
        
        # الإيرادات والمصاريف
        revenues = db.session.query(db.func.sum(Revenue.amount)).filter(
            Revenue.truck_id == truck_id,
            Revenue.revenue_date >= start_date
        ).scalar() or 0
        
        expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.truck_id == truck_id,
            Expense.expense_date >= start_date
        ).scalar() or 0
        
        profit = revenues - expenses
        
        # معدل الربحية
        profitability_rate = (profit / revenues * 100) if revenues > 0 else 0
        
        # متوسط الإيراد لكل شحنة
        avg_revenue_per_shipment = (revenues / total_shipments) if total_shipments > 0 else 0
        
        return {
            'truck_id': truck_id,
            'period_days': days,
            'total_shipments': total_shipments,
            'delivered_shipments': delivered_shipments,
            'delivery_rate': (delivered_shipments / total_shipments * 100) if total_shipments > 0 else 0,
            'total_revenue': float(revenues),
            'total_expenses': float(expenses),
            'profit': float(profit),
            'profitability_rate': float(profitability_rate),
            'avg_revenue_per_shipment': float(avg_revenue_per_shipment)
        }
    
    @staticmethod
    def get_driver_performance_metrics(driver_id, days=30):
        """حساب مقاييس أداء السائق"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # عدد الشحنات
        shipments = Shipment.query.filter(
            Shipment.driver_id == driver_id,
            Shipment.shipment_date >= start_date
        ).all()
        
        total_shipments = len(shipments)
        delivered_shipments = len([s for s in shipments if s.status == 'delivered'])
        
        # إجمالي الإيرادات
        total_revenue = sum([s.revenue for s in shipments])
        
        # المصاريف المرتبطة بالسائق
        expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.driver_id == driver_id,
            Expense.expense_date >= start_date
        ).scalar() or 0
        
        return {
            'driver_id': driver_id,
            'period_days': days,
            'total_shipments': total_shipments,
            'delivered_shipments': delivered_shipments,
            'delivery_rate': (delivered_shipments / total_shipments * 100) if total_shipments > 0 else 0,
            'total_revenue': float(total_revenue),
            'total_expenses': float(expenses),
            'net_contribution': float(total_revenue - expenses)
        }
    
    @staticmethod
    def get_fleet_efficiency_report(days=30):
        """تقرير كفاءة الأسطول"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        trucks = Truck.query.all()
        fleet_data = []
        
        for truck in trucks:
            metrics = AdvancedAnalytics.get_truck_performance_metrics(truck.id, days)
            fleet_data.append(metrics)
        
        # حساب المتوسطات
        total_trucks = len(trucks)
        avg_profitability = sum([m['profitability_rate'] for m in fleet_data]) / total_trucks if total_trucks > 0 else 0
        avg_delivery_rate = sum([m['delivery_rate'] for m in fleet_data]) / total_trucks if total_trucks > 0 else 0
        
        total_fleet_revenue = sum([m['total_revenue'] for m in fleet_data])
        total_fleet_expenses = sum([m['total_expenses'] for m in fleet_data])
        total_fleet_profit = total_fleet_revenue - total_fleet_expenses
        
        return {
            'period_days': days,
            'total_trucks': total_trucks,
            'trucks_metrics': fleet_data,
            'fleet_summary': {
                'total_revenue': float(total_fleet_revenue),
                'total_expenses': float(total_fleet_expenses),
                'total_profit': float(total_fleet_profit),
                'avg_profitability_rate': float(avg_profitability),
                'avg_delivery_rate': float(avg_delivery_rate)
            }
        }
    
    @staticmethod
    def get_expense_analysis(days=30):
        """تحليل المصاريف"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        expenses = Expense.query.filter(
            Expense.expense_date >= start_date
        ).all()
        
        # تجميع المصاريف حسب النوع
        expense_by_type = {}
        for expense in expenses:
            if expense.expense_type not in expense_by_type:
                expense_by_type[expense.expense_type] = 0
            expense_by_type[expense.expense_type] += expense.amount
        
        # تجميع المصاريف حسب القاطرة
        expense_by_truck = {}
        for expense in expenses:
            if expense.truck_id not in expense_by_truck:
                expense_by_truck[expense.truck_id] = 0
            expense_by_truck[expense.truck_id] += expense.amount
        
        total_expenses = sum([e.amount for e in expenses])
        
        return {
            'period_days': days,
            'total_expenses': float(total_expenses),
            'expenses_by_type': {k: float(v) for k, v in expense_by_type.items()},
            'expenses_by_truck': {k: float(v) for k, v in expense_by_truck.items()}
        }


class DataValidation:
    """التحقق من صحة البيانات والقيود"""
    
    @staticmethod
    def validate_truck_data(data):
        """التحقق من بيانات القاطرة"""
        errors = []
        
        if not data.get('truck_type'):
            errors.append('نوع القاطرة مطلوب')
        
        if not data.get('plate_number'):
            errors.append('رقم اللوحة مطلوب')
        
        # التحقق من تفرد رقم اللوحة
        existing_truck = Truck.query.filter_by(
            plate_number=data.get('plate_number')
        ).first()
        if existing_truck:
            errors.append('رقم اللوحة موجود بالفعل')
        
        return errors
    
    @staticmethod
    def validate_driver_data(data):
        """التحقق من بيانات السائق"""
        errors = []
        
        if not data.get('name'):
            errors.append('اسم السائق مطلوب')
        
        if not data.get('phone_number'):
            errors.append('رقم الهاتف مطلوب')
        
        if not data.get('salary') or float(data.get('salary', 0)) <= 0:
            errors.append('الراتب يجب أن يكون أكبر من صفر')
        
        return errors
    
    @staticmethod
    def validate_shipment_data(data):
        """التحقق من بيانات الشحنة"""
        errors = []
        
        if not data.get('truck_id'):
            errors.append('القاطرة مطلوبة')
        
        if not data.get('driver_id'):
            errors.append('السائق مطلوب')
        
        if not data.get('from_location'):
            errors.append('موقع البداية مطلوب')
        
        if not data.get('to_location'):
            errors.append('موقع النهاية مطلوب')
        
        if not data.get('cargo'):
            errors.append('وصف الشحنة مطلوب')
        
        if not data.get('revenue') or float(data.get('revenue', 0)) <= 0:
            errors.append('الإيراد يجب أن يكون أكبر من صفر')
        
        return errors
