/**
 * Main JavaScript file for Cryptocurrency Wallet application
 */

/**
 * Copy text to clipboard
 * @param {string} elementId - ID of element containing text to copy
 */
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error(`Element with ID ${elementId} not found`);
        return;
    }
    
    const text = element.textContent || element.innerText;
    
    // Create temporary textarea
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    
    // Select and copy
    textarea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy', 'error');
    }
    
    document.body.removeChild(textarea);
}

/**
 * Show notification message
 * @param {string} message - Message to display
 * @param {string} type - Type of notification ('success', 'error', 'info')
 */
function showNotification(message, type = 'info') {
    // Check if notification container exists
    let container = document.getElementById('notificationContainer');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificationContainer';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.padding = '1rem 1.5rem';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '0.375rem';
    notification.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)';
    notification.style.backgroundColor = type === 'success' ? '#10b981' : 
                                        type === 'error' ? '#ef4444' : '#3b82f6';
    notification.style.color = 'white';
    notification.style.fontWeight = '500';
    notification.style.animation = 'slideIn 0.3s ease-out';
    
    container.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            container.removeChild(notification);
        }, 300);
    }, 3000);
}

/**
 * Format number with commas
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8
    });
}

/**
 * Format address for display
 * @param {string} address - Full address
 * @param {number} startChars - Number of characters to show at start
 * @param {number} endChars - Number of characters to show at end
 * @returns {string} Formatted address
 */
function formatAddress(address, startChars = 10, endChars = 8) {
    if (!address || address.length <= startChars + endChars) {
        return address;
    }
    return `${address.substring(0, startChars)}...${address.substring(address.length - endChars)}`;
}

/**
 * Validate wallet address format
 * @param {string} address - Address to validate
 * @returns {boolean} True if valid format
 */
function validateAddress(address) {
    // Basic validation: should start with 0x and be 42 characters
    const addressRegex = /^0x[a-fA-F0-9]{40}$/;
    return addressRegex.test(address);
}

/**
 * Validate amount
 * @param {number} amount - Amount to validate
 * @returns {object} Validation result {valid: boolean, error: string}
 */
function validateAmount(amount) {
    if (isNaN(amount) || amount <= 0) {
        return {
            valid: false,
            error: 'Amount must be a positive number'
        };
    }
    
    if (amount < 0.01) {
        return {
            valid: false,
            error: 'Amount must be at least 0.01'
        };
    }
    
    if (amount > 10000) {
        return {
            valid: false,
            error: 'Amount cannot exceed 10,000'
        };
    }
    
    return {
        valid: true,
        error: null
    };
}

/**
 * Format timestamp to readable date
 * @param {string} timestamp - ISO timestamp
 * @returns {string} Formatted date
 */
function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
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

/**
 * Handle API errors
 * @param {object} error - Error object
 * @returns {string} User-friendly error message
 */
function handleApiError(error) {
    if (error.response) {
        // Server responded with error
        return error.response.data.error || 'An error occurred';
    } else if (error.request) {
        // Request made but no response
        return 'Network error. Please check your connection.';
    } else {
        // Other errors
        return error.message || 'An unexpected error occurred';
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export functions for use in other scripts
window.cryptoWallet = {
    copyToClipboard,
    showNotification,
    formatNumber,
    formatAddress,
    validateAddress,
    validateAmount,
    formatDate,
    debounce,
    handleApiError
};