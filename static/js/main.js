// Main JavaScript file for the Scheduler application
// Handles HTMX interactions and UI enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Initialize HTMX indicators
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        // Show loading indicator
        const target = evt.target;
        if (target.dataset.loading) {
            const loadingElement = document.querySelector(target.dataset.loading);
            if (loadingElement) {
                loadingElement.classList.remove('hidden');
            }
        }
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        // Hide loading indicator
        const target = evt.target;
        if (target.dataset.loading) {
            const loadingElement = document.querySelector(target.dataset.loading);
            if (loadingElement) {
                loadingElement.classList.add('hidden');
            }
        }
    });

    // Handle form submissions with HTMX
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        if (evt.target.tagName === 'FORM') {
            // Disable submit button to prevent double submission
            const submitBtn = evt.target.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Saving...';
            }
        }
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.target.tagName === 'FORM') {
            // Re-enable submit button
            const submitBtn = evt.target.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Save';
            }
        }
    });

    // Handle success messages
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.xhr.status === 200) {
            const response = evt.detail.xhr.response;
            if (response.includes('success')) {
                // Show success message
                showNotification('Operation completed successfully', 'success');
            }
        }
    });

    // Handle error messages
    document.body.addEventListener('htmx:responseError', function(evt) {
        showNotification('An error occurred. Please try again.', 'error');
    });
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-md shadow-lg max-w-sm ${
        type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' :
        type === 'error' ? 'bg-red-50 border border-red-200 text-red-800' :
        type === 'warning' ? 'bg-yellow-50 border border-yellow-200 text-yellow-800' :
        'bg-blue-50 border border-blue-200 text-blue-800'
    }`;
    
    notification.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                ${type === 'success' ? 
                    '<svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>' :
                    type === 'error' ?
                    '<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>' :
                    '<svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" /></svg>'
                }
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium">${message}</p>
            </div>
            <div class="ml-auto pl-3">
                <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                    <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Calendar functionality
function initCalendar() {
    // Calendar navigation
    const prevBtn = document.querySelector('[data-calendar-prev]');
    const nextBtn = document.querySelector('[data-calendar-next]');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            // HTMX will handle the navigation
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            // HTMX will handle the navigation
        });
    }
}

// Form validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

// Initialize calendar on page load
document.addEventListener('DOMContentLoaded', initCalendar);
