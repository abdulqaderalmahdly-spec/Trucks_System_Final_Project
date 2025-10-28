"""
نظام حساب السائق - حساب الرصيد والديون والمستحقات
"""

from models import db, Driver, Shipment, Expense, Revenue
from datetime import datetime

def calculate_driver_account(driver_id):
    """
    حساب كشف حساب السائق الكامل
    يشمل: الراتب، المصروفات، الإيرادات، والرصيد النهائي
    """
    driver = Driver.query.get(driver_id)
    if not driver:
        return None
    
    # حساب إجمالي الرواتب المستحقة
    total_salary = driver.salary  # الراتب الشهري الأساسي
    
    # حساب المصاريف المتعلقة بالسائق
    driver_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
        Expense.driver_id == driver_id
    ).scalar() or 0
    
    # حساب الإيرادات من الشحنات التي قام بها السائق
    driver_shipments = Shipment.query.filter_by(driver_id=driver_id).all()
    total_revenue = sum([shipment.revenue for shipment in driver_shipments])
    
    # حساب إجمالي المصاريف المتعلقة بقاطرة السائق
    if driver.truck_id:
        truck_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.truck_id == driver.truck_id
        ).scalar() or 0
    else:
        truck_expenses = 0
    
    # حساب عدد الشحنات
    shipment_count = len(driver_shipments)
    
    # حساب الرصيد النهائي
    # الرصيد = الإيرادات - (الراتب + المصاريف الشخصية)
    balance = total_revenue - (total_salary + driver_expenses)
    
    # تحديد حالة الحساب (دائن أو مدين)
    if balance > 0:
        account_status = 'دائن'  # الشركة مدينة للسائق
    elif balance < 0:
        account_status = 'مدين'  # السائق مدين للشركة
    else:
        account_status = 'متوازن'
    
    return {
        'driver_id': driver_id,
        'driver_name': driver.name,
        'phone_number': driver.phone_number,
        'truck_id': driver.truck_id,
        'salary': float(total_salary),
        'shipment_count': shipment_count,
        'total_revenue': float(total_revenue),
        'driver_expenses': float(driver_expenses),
        'truck_expenses': float(truck_expenses),
        'total_expenses': float(driver_expenses + truck_expenses),
        'balance': float(balance),
        'account_status': account_status,
        'is_active': driver.status == 'active'
    }


def get_driver_account_details(driver_id):
    """
    الحصول على تفاصيل كاملة لحساب السائق
    يشمل: قائمة الشحنات والمصاريف والرصيد
    """
    driver = Driver.query.get(driver_id)
    if not driver:
        return None
    
    # الحصول على بيانات الحساب الأساسية
    account_data = calculate_driver_account(driver_id)
    
    # الحصول على تفاصيل الشحنات
    shipments = Shipment.query.filter_by(driver_id=driver_id).all()
    shipments_data = [
        {
            'id': s.id,
            'from': s.from_location,
            'to': s.to_location,
            'cargo': s.cargo,
            'revenue': float(s.revenue),
            'status': s.status,
            'date': s.shipment_date.isoformat()
        }
        for s in shipments
    ]
    
    # الحصول على تفاصيل المصاريف
    expenses = Expense.query.filter_by(driver_id=driver_id).all()
    expenses_data = [
        {
            'id': e.id,
            'type': e.expense_type,
            'amount': float(e.amount),
            'description': e.description,
            'date': e.expense_date.isoformat()
        }
        for e in expenses
    ]
    
    return {
        'account': account_data,
        'shipments': shipments_data,
        'expenses': expenses_data
    }


def get_all_drivers_accounts():
    """
    الحصول على كشف حساب جميع السائقين
    """
    drivers = Driver.query.all()
    return [calculate_driver_account(driver.id) for driver in drivers]


def get_drivers_summary():
    """
    الحصول على ملخص إحصائي لجميع السائقين
    """
    drivers = Driver.query.all()
    
    total_drivers = len(drivers)
    active_drivers = len([d for d in drivers if d.status == 'active'])
    
    all_accounts = [calculate_driver_account(d.id) for d in drivers]
    
    total_revenue = sum([acc['total_revenue'] for acc in all_accounts])
    total_expenses = sum([acc['total_expenses'] for acc in all_accounts])
    total_balance = sum([acc['balance'] for acc in all_accounts])
    
    creditor_drivers = len([acc for acc in all_accounts if acc['account_status'] == 'دائن'])
    debtor_drivers = len([acc for acc in all_accounts if acc['account_status'] == 'مدين'])
    
    return {
        'total_drivers': total_drivers,
        'active_drivers': active_drivers,
        'total_revenue': float(total_revenue),
        'total_expenses': float(total_expenses),
        'total_balance': float(total_balance),
        'creditor_drivers': creditor_drivers,
        'debtor_drivers': debtor_drivers,
        'drivers': all_accounts
    }
