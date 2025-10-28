"""
المسارات الجديدة للميزات المتقدمة
"""

from flask import Blueprint, request, jsonify
from advanced_features import NotificationSystem, AdvancedAnalytics, DataValidation
from models import db, Notification

# إنشاء Blueprint للمسارات المتقدمة
advanced_bp = Blueprint('advanced', __name__, url_prefix='/api/advanced')

# ============ مسارات نظام الإشعارات ============

@advanced_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """الحصول على الإشعارات غير المقروءة"""
    notifications = NotificationSystem.get_unread_notifications()
    return jsonify({
        'count': len(notifications),
        'notifications': notifications
    })

@advanced_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """تحديد الإشعار كمقروء"""
    success = NotificationSystem.mark_notification_as_read(notification_id)
    if success:
        return jsonify({'message': 'تم تحديث الإشعار'})
    return jsonify({'error': 'الإشعار غير موجود'}), 404

@advanced_bp.route('/notifications/check-maintenance/<int:truck_id>', methods=['POST'])
def check_maintenance(truck_id):
    """التحقق من الصيانة المستحقة"""
    days_threshold = request.args.get('days', 30, type=int)
    is_due = NotificationSystem.check_maintenance_due(truck_id, days_threshold)
    return jsonify({
        'truck_id': truck_id,
        'maintenance_due': is_due,
        'threshold_days': days_threshold
    })

@advanced_bp.route('/notifications/check-profitability/<int:truck_id>', methods=['POST'])
def check_profitability(truck_id):
    """التحقق من ربحية القاطرة"""
    days = request.args.get('days', 30, type=int)
    is_profitable = NotificationSystem.check_truck_profitability(truck_id, days)
    return jsonify({
        'truck_id': truck_id,
        'is_profitable': is_profitable,
        'period_days': days
    })

# ============ مسارات التحليلات المتقدمة ============

@advanced_bp.route('/analytics/truck-performance/<int:truck_id>', methods=['GET'])
def get_truck_performance(truck_id):
    """الحصول على مقاييس أداء القاطرة"""
    days = request.args.get('days', 30, type=int)
    metrics = AdvancedAnalytics.get_truck_performance_metrics(truck_id, days)
    return jsonify(metrics)

@advanced_bp.route('/analytics/driver-performance/<int:driver_id>', methods=['GET'])
def get_driver_performance(driver_id):
    """الحصول على مقاييس أداء السائق"""
    days = request.args.get('days', 30, type=int)
    metrics = AdvancedAnalytics.get_driver_performance_metrics(driver_id, days)
    return jsonify(metrics)

@advanced_bp.route('/analytics/fleet-efficiency', methods=['GET'])
def get_fleet_efficiency():
    """الحصول على تقرير كفاءة الأسطول"""
    days = request.args.get('days', 30, type=int)
    report = AdvancedAnalytics.get_fleet_efficiency_report(days)
    return jsonify(report)

@advanced_bp.route('/analytics/expense-analysis', methods=['GET'])
def get_expense_analysis():
    """الحصول على تحليل المصاريف"""
    days = request.args.get('days', 30, type=int)
    analysis = AdvancedAnalytics.get_expense_analysis(days)
    return jsonify(analysis)

# ============ مسارات التحقق من البيانات ============

@advanced_bp.route('/validate/truck', methods=['POST'])
def validate_truck():
    """التحقق من بيانات القاطرة"""
    data = request.get_json()
    errors = DataValidation.validate_truck_data(data)
    
    if errors:
        return jsonify({'valid': False, 'errors': errors}), 400
    return jsonify({'valid': True, 'message': 'البيانات صحيحة'})

@advanced_bp.route('/validate/driver', methods=['POST'])
def validate_driver():
    """التحقق من بيانات السائق"""
    data = request.get_json()
    errors = DataValidation.validate_driver_data(data)
    
    if errors:
        return jsonify({'valid': False, 'errors': errors}), 400
    return jsonify({'valid': True, 'message': 'البيانات صحيحة'})

@advanced_bp.route('/validate/shipment', methods=['POST'])
def validate_shipment():
    """التحقق من بيانات الشحنة"""
    data = request.get_json()
    errors = DataValidation.validate_shipment_data(data)
    
    if errors:
        return jsonify({'valid': False, 'errors': errors}), 400
    return jsonify({'valid': True, 'message': 'البيانات صحيحة'})
