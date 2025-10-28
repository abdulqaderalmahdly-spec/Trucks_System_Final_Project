// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Utility Functions
async function fetchAPI(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showAlert('حدث خطأ في الاتصال بالخادم', 'error');
        throw error;
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: 'SAR'
    }).format(amount);
}

// Trucks Management
async function loadTrucks() {
    try {
        const trucks = await fetchAPI('/trucks');
        const tbody = document.querySelector('#trucksTable tbody');
        
        if (tbody) {
            tbody.innerHTML = trucks.map(truck => `
                <tr>
                    <td>${truck.plate_number}</td>
                    <td>${truck.truck_type}</td>
                    <td><span class="badge badge-${truck.status}">${truck.status}</span></td>
                    <td>${formatDate(truck.last_maintenance_date)}</td>
                    <td>${truck.total_shipments}</td>
                    <td>
                        <button onclick="editTruck(${truck.id})" class="btn btn-primary">تعديل</button>
                        <button onclick="deleteTruck(${truck.id})" class="btn btn-danger">حذف</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading trucks:', error);
    }
}

async function createTruck() {
    const form = document.querySelector('#truckForm');
    if (!form) return;
    
    const data = {
        truck_type: form.truck_type.value,
        plate_number: form.plate_number.value,
        status: form.status.value
    };
    
    try {
        await fetchAPI('/trucks', 'POST', data);
        showAlert('تم إضافة القاطرة بنجاح', 'success');
        form.reset();
        loadTrucks();
        closeModal('truckModal');
    } catch (error) {
        console.error('Error creating truck:', error);
    }
}

async function deleteTruck(id) {
    if (confirm('هل أنت متأكد من حذف هذه القاطرة؟')) {
        try {
            await fetchAPI(`/trucks/${id}`, 'DELETE');
            showAlert('تم حذف القاطرة بنجاح', 'success');
            loadTrucks();
        } catch (error) {
            console.error('Error deleting truck:', error);
        }
    }
}

// Drivers Management
async function loadDrivers() {
    try {
        const drivers = await fetchAPI('/drivers');
        const tbody = document.querySelector('#driversTable tbody');
        
        if (tbody) {
            tbody.innerHTML = drivers.map(driver => `
                <tr>
                    <td>${driver.name}</td>
                    <td>${driver.phone_number}</td>
                    <td>${formatCurrency(driver.salary)}</td>
                    <td><span class="badge badge-${driver.status}">${driver.status}</span></td>
                    <td>
                        <button onclick="editDriver(${driver.id})" class="btn btn-primary">تعديل</button>
                        <button onclick="deleteDriver(${driver.id})" class="btn btn-danger">حذف</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading drivers:', error);
    }
}

async function createDriver() {
    const form = document.querySelector('#driverForm');
    if (!form) return;
    
    const data = {
        name: form.name.value,
        phone_number: form.phone_number.value,
        salary: parseFloat(form.salary.value),
        truck_id: parseInt(form.truck_id.value),
        status: form.status.value
    };
    
    try {
        await fetchAPI('/drivers', 'POST', data);
        showAlert('تم إضافة السائق بنجاح', 'success');
        form.reset();
        loadDrivers();
        closeModal('driverModal');
    } catch (error) {
        console.error('Error creating driver:', error);
    }
}

async function deleteDriver(id) {
    if (confirm('هل أنت متأكد من حذف هذا السائق؟')) {
        try {
            await fetchAPI(`/drivers/${id}`, 'DELETE');
            showAlert('تم حذف السائق بنجاح', 'success');
            loadDrivers();
        } catch (error) {
            console.error('Error deleting driver:', error);
        }
    }
}

// Shipments Management
async function loadShipments() {
    try {
        const shipments = await fetchAPI('/shipments');
        const tbody = document.querySelector('#shipmentsTable tbody');
        
        if (tbody) {
            tbody.innerHTML = shipments.map(shipment => `
                <tr>
                    <td>${shipment.from_location}</td>
                    <td>${shipment.to_location}</td>
                    <td>${shipment.cargo}</td>
                    <td>${formatCurrency(shipment.revenue)}</td>
                    <td><span class="badge badge-${shipment.status}">${shipment.status}</span></td>
                    <td>
                        <button onclick="updateShipmentStatus(${shipment.id})" class="btn btn-primary">تحديث</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading shipments:', error);
    }
}

async function createShipment() {
    const form = document.querySelector('#shipmentForm');
    if (!form) return;
    
    const data = {
        truck_id: parseInt(form.truck_id.value),
        driver_id: parseInt(form.driver_id.value),
        from_location: form.from_location.value,
        to_location: form.to_location.value,
        cargo: form.cargo.value,
        revenue: parseFloat(form.revenue.value),
        status: form.status.value
    };
    
    try {
        await fetchAPI('/shipments', 'POST', data);
        showAlert('تم إضافة الشحنة بنجاح', 'success');
        form.reset();
        loadShipments();
        closeModal('shipmentModal');
    } catch (error) {
        console.error('Error creating shipment:', error);
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const data = await fetchAPI('/dashboard');
        
        // Update stats
        document.querySelector('#totalTrucks').textContent = data.trucks.total;
        document.querySelector('#activeTrucks').textContent = data.trucks.active;
        document.querySelector('#totalDrivers').textContent = data.drivers.total;
        document.querySelector('#totalShipments').textContent = data.shipments.total;
        document.querySelector('#totalRevenue').textContent = formatCurrency(data.financials.revenue);
        document.querySelector('#totalExpenses').textContent = formatCurrency(data.financials.expenses);
        document.querySelector('#totalProfit').textContent = formatCurrency(data.financials.profit);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Modal Functions
function openModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
    }
}

// Load trucks on page load
document.addEventListener('DOMContentLoaded', function() {
    const page = document.body.getAttribute('data-page');
    
    if (page === 'trucks') {
        loadTrucks();
    } else if (page === 'drivers') {
        loadDrivers();
    } else if (page === 'shipments') {
        loadShipments();
    } else if (page === 'dashboard') {
        loadDashboard();
        // Refresh dashboard every 30 seconds
        setInterval(loadDashboard, 30000);
    }
});
