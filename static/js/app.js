// Main JavaScript for PQRS RAG System

// API Base URL
const API_BASE = '/api/v1';

// Utility functions
const Utils = {
    // Show loading modal
    showLoading: function(title = 'Procesando...', subtitle = 'Por favor espere') {
        const modal = document.getElementById('loadingModal');
        if (modal) {
            const titleEl = modal.querySelector('h5');
            const subtitleEl = modal.querySelector('.text-muted');
            if (titleEl) titleEl.textContent = title;
            if (subtitleEl) subtitleEl.textContent = subtitle;
            
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }
    },

    // Hide loading modal
    hideLoading: function() {
        const modal = document.getElementById('loadingModal');
        if (modal) {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        }
    },

    // Show alert
    showAlert: function(message, type = 'info', container = null) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-info-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        if (container) {
            container.innerHTML = alertHtml;
        } else {
            // Create temporary alert at top of page
            const tempContainer = document.createElement('div');
            tempContainer.className = 'container mt-3';
            tempContainer.innerHTML = alertHtml;
            document.body.insertBefore(tempContainer, document.body.firstChild);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                tempContainer.remove();
            }, 5000);
        }
    },

    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CO', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Format confidence percentage
    formatConfidence: function(confidence) {
        return Math.round(confidence * 100) + '%';
    },

    // Get confidence color
    getConfidenceColor: function(confidence) {
        if (confidence >= 0.8) return 'success';
        if (confidence >= 0.6) return 'warning';
        return 'danger';
    },

    // Sanitize HTML
    sanitizeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Format category name
    formatCategoryName: function(category) {
        return category.replace(/_/g, ' ').toLowerCase()
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    },

    // API request wrapper
    apiRequest: async function(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // Form data to object
    formDataToObject: function(formData) {
        const object = {};
        formData.forEach((value, key) => {
            if (value !== '') {
                object[key] = value;
            }
        });
        return object;
    }
};

// Category Management
const CategoryManager = {
    categories: [],

    // Load categories from API
    loadCategories: async function() {
        try {
            const response = await Utils.apiRequest('/categories');
            this.categories = response.categorias;
            return this.categories;
        } catch (error) {
            console.error('Error loading categories:', error);
            return [];
        }
    },

    // Populate select element with categories
    populateSelect: function(selectElement, includeEmpty = true) {
        if (!selectElement) return;

        selectElement.innerHTML = '';
        
        if (includeEmpty) {
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = 'Seleccione categoría...';
            selectElement.appendChild(emptyOption);
        }

        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.valor;
            option.textContent = category.nombre;
            option.title = category.descripcion;
            selectElement.appendChild(option);
        });
    },

    // Get category by value
    getCategoryByValue: function(value) {
        return this.categories.find(cat => cat.valor === value);
    }
};

// Notification system
const NotificationSystem = {
    show: function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        const icon = this.getIcon(type);
        notification.innerHTML = `
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove
        setTimeout(() => {
            notification.remove();
        }, duration);
    },

    getIcon: function(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'danger': 'fas fa-times-circle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    // Load categories
    await CategoryManager.loadCategories();
    
    // Populate category selects
    const categorySelects = document.querySelectorAll('#categoriaSelect, #uploadCategoria, #searchCategoria');
    categorySelects.forEach(select => {
        if (select.id === 'searchCategoria') {
            CategoryManager.populateSelect(select, true);
            // Add "all categories" option for search
            const allOption = document.createElement('option');
            allOption.value = '';
            allOption.textContent = 'Todas las categorías';
            select.insertBefore(allOption, select.firstChild);
            select.selectedIndex = 0;
        } else {
            CategoryManager.populateSelect(select);
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert:not(.alert-persistent)').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    NotificationSystem.show(
        'Ha ocurrido un error inesperado. Por favor, recargue la página.',
        'danger',
        8000
    );
});

// Export utilities to global scope
window.Utils = Utils;
window.CategoryManager = CategoryManager;
window.NotificationSystem = NotificationSystem;