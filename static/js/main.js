// Main JavaScript for FoodChain Tracker
'use strict';

// Global variables
let refreshInterval;
let notificationTimeout;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeThemeToggle();
});

// Main initialization function
function initializeApp() {
    setupEventListeners();
    initializeTooltips();
    setupFormSubmissions();
    startAutoRefresh();
    setupNotifications();
    initializeCharts();
    setupSearchFunctionality();
}

// ===================================
// THEME TOGGLE FUNCTIONALITY
// ===================================

function initializeThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const body = document.body;
    
    // Check for saved theme preference or default to light
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the saved theme
    if (currentTheme === 'dark') {
        body.setAttribute('data-theme', 'dark');
        updateThemeToggleUI(true);
    } else {
        body.setAttribute('data-theme', 'light');
        updateThemeToggleUI(false);
    }
    
    // Theme toggle event listener
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isDark = body.getAttribute('data-theme') === 'dark';
            
            if (isDark) {
                // Switch to light theme
                body.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                updateThemeToggleUI(false);
                showThemeNotification('Light theme activated');
            } else {
                // Switch to dark theme
                body.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                updateThemeToggleUI(true);
                showThemeNotification('Dark theme activated');
            }
        });
    }
}

function updateThemeToggleUI(isDark) {
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    
    if (isDark) {
        themeIcon.className = 'fas fa-sun';
        if (themeText) themeText.textContent = 'Light';
    } else {
        themeIcon.className = 'fas fa-moon';
        if (themeText) themeText.textContent = 'Dark';
    }
}

function showThemeNotification(message) {
    // Use existing notification system if available
    if (typeof showNotification === 'function') {
        showNotification(message, 'info', 2000);
    } else {
        // Simple fallback notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-info position-fixed';
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 1050;
            min-width: 250px;
            animation: slideInRight 0.3s ease-out;
        `;
        notification.innerHTML = `
            <i class="fas fa-palette me-2"></i>${message}
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
}

// ===================================
// EXISTING FUNCTIONALITY
// ===================================

// Event Listeners
function setupEventListeners() {
    // Navigation active states
    updateActiveNavigation();
    
    // Form submissions with loading states
    setupFormSubmissions();
    
    // Copy to clipboard functionality
    setupClipboardActions();
    
    // Modal triggers
    setupModals();
    
    // Real-time updates
    setupRealtimeUpdates();
}

// Update active navigation item
function updateActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            link.classList.add('active');
            link.parentElement.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
            link.parentElement.classList.add('active');
        }
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation and submission
function setupFormSubmissions() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // Add loading state to submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                addLoadingState(submitBtn);
            }
        });
    });
}

// Form validation
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
            
            // Specific validations
            if (field.type === 'email' && !isValidEmail(field.value)) {
                showFieldError(field, 'Please enter a valid email address');
                isValid = false;
            }
            
            if (field.type === 'number') {
                const min = parseFloat(field.getAttribute('min'));
                const max = parseFloat(field.getAttribute('max'));
                const value = parseFloat(field.value);
                
                if (!isNaN(min) && value < min) {
                    showFieldError(field, `Value must be at least ${min}`);
                    isValid = false;
                }
                
                if (!isNaN(max) && value > max) {
                    showFieldError(field, `Value must be no more than ${max}`);
                    isValid = false;
                }
            }
        }
    });
    
    // Password confirmation validation
    const password = form.querySelector('input[name="password"]');
    const confirmPassword = form.querySelector('input[name="confirm_password"]');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
        showFieldError(confirmPassword, 'Passwords do not match');
        isValid = false;
    }
    
    return isValid;
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Add loading state to button
function addLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading-spinner me-2"></span>Processing...';
    button.disabled = true;
    
    // Store original text for restoration
    button.dataset.originalText = originalText;
}

// Remove loading state from button
function removeLoadingState(button) {
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
}

// Clipboard functionality
function setupClipboardActions() {
    const clipboardButtons = document.querySelectorAll('[data-clipboard-text]');
    
    clipboardButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.getAttribute('data-clipboard-text');
            copyToClipboard(text, this);
        });
    });
}

// Copy to clipboard
function copyToClipboard(text, button = null) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showCopySuccess(button);
        }).catch(function() {
            fallbackCopyToClipboard(text, button);
        });
    } else {
        fallbackCopyToClipboard(text, button);
    }
}

// Fallback copy method
function fallbackCopyToClipboard(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopySuccess(button);
    } catch (err) {
        console.error('Fallback: Could not copy text');
        showNotification('Failed to copy to clipboard', 'danger');
    }
    
    document.body.removeChild(textArea);
}

// Show copy success feedback
function showCopySuccess(button) {
    if (button) {
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
        button.classList.add('btn-success');
        
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.classList.remove('btn-success');
        }, 2000);
    }
    
    showNotification('Copied to clipboard!', 'success');
}

// Auto-refresh functionality
function startAutoRefresh() {
    // Refresh dashboard data every 30 seconds
    if (window.location.pathname.includes('/dashboard')) {
        refreshInterval = setInterval(refreshDashboardData, 30000);
    }
}

// Refresh dashboard data
function refreshDashboardData() {
    // Update statistics
    fetch('/dashboard/api/quick_stats')
        .then(response => response.json())
        .then(data => updateDashboardStats(data))
        .catch(error => console.error('Error refreshing dashboard:', error));
    
    // Update recent activities
    fetch('/dashboard/api/recent_activities')
        .then(response => response.json())
        .then(data => updateRecentActivities(data))
        .catch(error => console.error('Error refreshing activities:', error));
}

// Update dashboard statistics
function updateDashboardStats(data) {
    Object.keys(data).forEach(key => {
        const element = document.querySelector(`[data-stat="${key}"]`);
        if (element && data[key] !== undefined) {
            animateNumber(element, data[key]);
        }
    });
}

// Animate number changes
function animateNumber(element, newValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const increment = (newValue - currentValue) / 20;
    let current = currentValue;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= newValue) || (increment < 0 && current <= newValue)) {
            current = newValue;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 50);
}

// Notification system
function setupNotifications() {
    // Check for fraud alerts every 60 seconds
    if (window.location.pathname.includes('/analytics')) {
        setInterval(checkFraudAlerts, 60000);
    }
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    // Clear existing notification
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
    
    const existingNotification = document.querySelector('.floating-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} floating-notification position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    `;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    notificationTimeout = setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || icons.info;
}

// Check for fraud alerts
function checkFraudAlerts() {
    fetch('/analytics/api/fraud_alerts')
        .then(response => response.json())
        .then(alerts => {
            if (alerts.length > 0) {
                alerts.forEach(alert => {
                    if (alert.severity === 'high') {
                        showNotification(alert.message, 'danger', 10000);
                    }
                });
            }
        })
        .catch(error => console.error('Error checking fraud alerts:', error));
}

// Initialize charts
function initializeCharts() {
    // Initialize any Chart.js charts on the page
    const chartElements = document.querySelectorAll('canvas[data-chart]');
    
    chartElements.forEach(canvas => {
        const chartType = canvas.getAttribute('data-chart');
        const dataUrl = canvas.getAttribute('data-url');
        
        if (dataUrl) {
            fetch(dataUrl)
                .then(response => response.json())
                .then(data => createChart(canvas, chartType, data))
                .catch(error => console.error('Error loading chart data:', error));
        }
    });
}

// Create chart
function createChart(canvas, type, data) {
    const ctx = canvas.getContext('2d');
    
    const config = {
        type: type,
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    };
    
    new Chart(ctx, config);
}

// Search functionality
function setupSearchFunctionality() {
    const searchInputs = document.querySelectorAll('input[data-search]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                const searchType = this.getAttribute('data-search');
                
                if (query.length >= 2) {
                    performSearch(query, searchType);
                } else {
                    clearSearchResults();
                }
            }, 300);
        });
    });
}

// Perform search
function performSearch(query, type) {
    const url = `/api/search?q=${encodeURIComponent(query)}&type=${type}`;
    
    fetch(url)
        .then(response => response.json())
        .then(results => displaySearchResults(results))
        .catch(error => console.error('Search error:', error));
}

// Display search results
function displaySearchResults(results) {
    const resultsContainer = document.querySelector('#search-results');
    if (!resultsContainer) return;
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p class="text-muted">No results found.</p>';
        return;
    }
    
    let html = '<div class="list-group">';
    results.forEach(result => {
        html += `
            <a href="${result.url}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${result.title}</h6>
                    <small>${result.type}</small>
                </div>
                <p class="mb-1">${result.description}</p>
            </a>
        `;
    });
    html += '</div>';
    
    resultsContainer.innerHTML = html;
}

// Setup modals
function setupModals() {
    const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.getAttribute('data-bs-target');
            const modal = document.querySelector(modalId);
            
            if (modal) {
                // Load dynamic content if specified
                const dataUrl = this.getAttribute('data-url');
                if (dataUrl) {
                    loadModalContent(modal, dataUrl);
                }
            }
        });
    });
}

// Load modal content
function loadModalContent(modal, url) {
    const modalBody = modal.querySelector('.modal-body');
    
    modalBody.innerHTML = '<div class="text-center"><div class="loading-spinner"></div> Loading...</div>';
    
    fetch(url)
        .then(response => response.text())
        .then(html => {
            modalBody.innerHTML = html;
        })
        .catch(error => {
            modalBody.innerHTML = '<div class="alert alert-danger">Error loading content.</div>';
            console.error('Modal content error:', error);
        });
}

// Setup real-time updates
function setupRealtimeUpdates() {
    // WebSocket connection for real-time updates (if implemented)
    // This is a placeholder for future real-time functionality
    
    // For now, use polling for live updates
    if (window.location.pathname.includes('/products/')) {
        setInterval(updateProductStatus, 60000);
    }
}

// Update product status
function updateProductStatus() {
    const productId = document.querySelector('[data-product-id]')?.getAttribute('data-product-id');
    
    if (productId) {
        fetch(`/products/api/${productId}/track`)
            .then(response => response.json())
            .then(data => {
                updateProductDisplay(data);
            })
            .catch(error => console.error('Product update error:', error));
    }
}

// Update product display
function updateProductDisplay(data) {
    // Update environmental conditions
    if (data.environmental_conditions) {
        const tempElement = document.querySelector('[data-temp]');
        const humidityElement = document.querySelector('[data-humidity]');
        
        if (tempElement && data.environmental_conditions.temperature) {
            tempElement.textContent = `${data.environmental_conditions.temperature}°C`;
        }
        
        if (humidityElement && data.environmental_conditions.humidity) {
            humidityElement.textContent = `${data.environmental_conditions.humidity}%`;
        }
    }
    
    // Update status
    const statusElement = document.querySelector('[data-status]');
    if (statusElement && data.status) {
        statusElement.textContent = data.status;
        statusElement.className = `badge bg-${getStatusColor(data.status)}`;
    }
}

// Get status color
function getStatusColor(status) {
    const colors = {
        'created': 'success',
        'in_transit': 'warning',
        'delivered': 'info',
        'expired': 'danger'
    };
    return colors[status] || 'secondary';
}

// Cleanup when page unloads
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
});

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for global use
window.FoodChainTracker = {
    showNotification,
    copyToClipboard,
    refreshDashboardData,
    updateProductStatus,
    initializeThemeToggle
};

// Clear search results
function clearSearchResults() {
    const resultsContainer = document.querySelector('#search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = '';
    }
}

// Update recent activities
function updateRecentActivities(data) {
    const activitiesContainer = document.querySelector('#recent-activities');
    if (!activitiesContainer) return;
    
    if (data.length === 0) {
        activitiesContainer.innerHTML = '<p class="text-muted">No recent activities found.</p>';
        return;
    }
    
    let html = '<div class="timeline">';
    data.forEach(activity => {
        html += `
            <div class="timeline-item d-flex mb-3">
                <div class="timeline-marker">
                    <i class="fas fa-${activity.icon || 'circle'} text-${activity.type || 'primary'}"></i>
                </div>
                <div class="timeline-content ms-3">
                    <h6 class="mb-1">${activity.description}</h6>
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>
                        ${activity.timestamp}
                    </small>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    activitiesContainer.innerHTML = html;
}

// Batch ID copy functionality
function copyBatchId(batchId) {
    copyToClipboard(batchId);
}

// Product status tracking
function trackProduct(productId) {
    if (!productId) return;
    
    fetch(`/products/api/${productId}/track`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateProductDisplay(data.product);
                showNotification('Product status updated', 'success');
            }
        })
        .catch(error => {
            console.error('Product tracking error:', error);
            showNotification('Failed to update product status', 'danger');
        });
}

// Form enhancement for file uploads
function setupFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const label = this.nextElementSibling;
            
            if (fileName && label) {
                label.textContent = fileName;
                label.classList.add('text-success');
            }
        });
    });
}

// Enhanced form validation with real-time feedback
function setupRealtimeValidation() {
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const isRequired = field.hasAttribute('required');
    
    // Clear previous validation
    clearFieldError(field);
    
    // Required field validation
    if (isRequired && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    // Email validation
    if (field.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
        return false;
    }
    
    // Number validation
    if (field.type === 'number' && value) {
        const min = parseFloat(field.getAttribute('min'));
        const max = parseFloat(field.getAttribute('max'));
        const numValue = parseFloat(value);
        
        if (!isNaN(min) && numValue < min) {
            showFieldError(field, `Value must be at least ${min}`);
            return false;
        }
        
        if (!isNaN(max) && numValue > max) {
            showFieldError(field, `Value must be no more than ${max}`);
            return false;
        }
    }
    
    // Show success state
    field.classList.add('is-valid');
    return true;
}

// QR Code functionality
function generateQRCode(productId) {
    if (!productId) return;
    
    window.open(`/products/${productId}/qr-code`, '_blank');
}

// Print functionality
function printPage() {
    window.print();
}

function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Print</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { font-family: Arial, sans-serif; }
                @media print {
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${element.innerHTML}
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Data export functionality
function exportData(format, data, filename) {
    if (format === 'csv') {
        exportToCSV(data, filename);
    } else if (format === 'json') {
        exportToJSON(data, filename);
    }
}

function exportToCSV(data, filename) {
    if (!data || data.length === 0) return;
    
    const csvContent = [
        Object.keys(data[0]).join(','),
        ...data.map(row => Object.values(row).join(','))
    ].join('\n');
    
    downloadFile(csvContent, `${filename}.csv`, 'text/csv');
}

function exportToJSON(data, filename) {
    const jsonContent = JSON.stringify(data, null, 2);
    downloadFile(jsonContent, `${filename}.json`, 'application/json');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

// Geolocation functionality
function getCurrentLocation(callback) {
    if (!navigator.geolocation) {
        showNotification('Geolocation is not supported by this browser', 'warning');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        position => {
            const { latitude, longitude } = position.coords;
            callback({ latitude, longitude });
        },
        error => {
            console.error('Geolocation error:', error);
            showNotification('Unable to get your location', 'warning');
        }
    );
}

// Auto-fill location fields
function fillLocationFields() {
    getCurrentLocation(location => {
        const latField = document.getElementById('latitude');
        const lngField = document.getElementById('longitude');
        
        if (latField) latField.value = location.latitude.toFixed(6);
        if (lngField) lngField.value = location.longitude.toFixed(6);
        
        showNotification('Location filled automatically', 'success');
    });
}

// Blockchain verification
function verifyBlockchainRecord(recordId) {
    if (!recordId) return;
    
    fetch(`/api/blockchain/verify/${recordId}`)
        .then(response => response.json())
        .then(data => {
            if (data.verified) {
                showNotification('Blockchain record verified successfully', 'success');
            } else {
                showNotification('Blockchain verification failed', 'danger');
            }
        })
        .catch(error => {
            console.error('Verification error:', error);
            showNotification('Error verifying blockchain record', 'danger');
        });
}

// Advanced search functionality
function setupAdvancedSearch() {
    const searchForm = document.getElementById('advanced-search-form');
    if (!searchForm) return;
    
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const searchParams = new URLSearchParams();
        
        for (const [key, value] of formData.entries()) {
            if (value.trim()) {
                searchParams.append(key, value);
            }
        }
        
        fetch(`/api/advanced-search?${searchParams}`)
            .then(response => response.json())
            .then(data => {
                displaySearchResults(data);
                showNotification(`Found ${data.length} results`, 'info');
            })
            .catch(error => {
                console.error('Advanced search error:', error);
                showNotification('Search failed', 'danger');
            });
    });
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + D for dark mode toggle
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            const themeToggle = document.getElementById('themeToggle');
            if (themeToggle) {
                themeToggle.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modalInstance = bootstrap.Modal.getInstance(openModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
    });
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    setupFileUploads();
    setupRealtimeValidation();
    setupAdvancedSearch();
    setupKeyboardShortcuts();
});

// Add CSS for animations and additional styling
const style = document.createElement('style');
style.textContent = `
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

@keyframes fadeInUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.animate-fade-in-up {
    animation: fadeInUp 0.5s ease-out;
}

.hover-scale {
    transition: transform 0.2s ease;
}

.hover-scale:hover {
    transform: scale(1.02);
}

.timeline {
    position: relative;
    padding-left: 2rem;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 0.75rem;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--primary);
    opacity: 0.3;
}

.timeline-marker {
    position: absolute;
    left: -1.5rem;
    width: 1.5rem;
    height: 1.5rem;
    background: var(--bg-card);
    border: 2px solid var(--primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.pulse {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
    100% {
        transform: scale(1);
    }
}
`;
document.head.appendChild(style);