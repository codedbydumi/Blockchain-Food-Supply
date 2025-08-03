// Main JavaScript for FoodChain Tracker
'use strict';

// Global variables
let refreshInterval;
let notificationTimeout;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    setupEventListeners();
    initializeTooltips();
    setupFormSubmissions();  // ← Changed from setupFormValidation
    startAutoRefresh();
    setupNotifications();
    initializeCharts();
    setupSearchFunctionality();
}
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
    updateProductStatus
};