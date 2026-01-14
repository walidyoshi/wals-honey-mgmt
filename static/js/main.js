/**
 * Main JavaScript for Honey Management System
 */

document.addEventListener('DOMContentLoaded', function () {

    // Auto-calculate total price in Sale form
    const form = document.getElementById('sale-form');
    if (form) {
        const unitPriceInput = document.getElementById('id_unit_price');
        const quantityInput = document.getElementById('id_quantity');
        const totalPriceDisplay = document.getElementById('total-price-display');

        function calculateTotal() {
            // Parse formatted values (remove commas)
            const priceValue = unitPriceInput.value.replace(/,/g, '');
            const qtyValue = quantityInput.value.replace(/,/g, '');

            const price = parseFloat(priceValue) || 0;
            const qty = parseFloat(qtyValue) || 0;
            const total = price * qty;

            if (totalPriceDisplay) {
                totalPriceDisplay.textContent = '₦' + total.toLocaleString('en-NG', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
        }

        if (unitPriceInput && quantityInput) {
            unitPriceInput.addEventListener('input', calculateTotal);
            quantityInput.addEventListener('input', calculateTotal);
        }
    }

    // Auto-dismiss alerts
    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);

    // HTMX config
    document.body.addEventListener('htmx:configRequest', (event) => {
        event.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
    });

    // ========================================
    // Number Input Formatting & Validation
    // ========================================

    /**
     * Format a number with thousand separators
     * @param {string|number} value - The value to format
     * @param {number} decimals - Number of decimal places (default: 2)
     * @returns {string} Formatted number string
     */
    function formatNumber(value, decimals = 2) {
        // Remove existing formatting
        const cleanValue = String(value).replace(/,/g, '');
        const num = parseFloat(cleanValue);

        if (isNaN(num)) return '';

        return num.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    /**
     * Parse a formatted number string to a plain number string
     * @param {string} value - The formatted value
     * @returns {string} Plain number string
     */
    function parseFormattedNumber(value) {
        return String(value).replace(/,/g, '');
    }

    /**
     * Validate and clean numeric input
     * @param {string} value - The input value
     * @param {boolean} allowDecimals - Whether to allow decimal points
     * @returns {string} Cleaned value
     */
    function cleanNumericInput(value, allowDecimals = true) {
        let cleaned = value.replace(/[^\d.]/g, '');

        if (!allowDecimals) {
            cleaned = cleaned.replace(/\./g, '');
        } else {
            // Allow only one decimal point
            const parts = cleaned.split('.');
            if (parts.length > 2) {
                cleaned = parts[0] + '.' + parts.slice(1).join('');
            }
        }

        return cleaned;
    }

    // Handle currency inputs (prices, costs, amounts)
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(input => {
        // Store the raw value
        let rawValue = parseFormattedNumber(input.value || '0');

        // Format on blur
        input.addEventListener('blur', function () {
            const cleaned = cleanNumericInput(this.value, true);
            if (cleaned === '' || cleaned === '.') {
                rawValue = '';
                this.value = '';
            } else {
                rawValue = cleaned;
                this.value = formatNumber(cleaned, 2);
            }
        });

        // Remove formatting on focus for easy editing
        input.addEventListener('focus', function () {
            const cleaned = parseFormattedNumber(this.value);
            this.value = cleaned === '0' ? '' : cleaned;
            this.select();
        });

        // Clean input in real-time (prevent alphabets)
        input.addEventListener('input', function (e) {
            const cursorPos = this.selectionStart;
            const oldValue = this.value;
            const cleaned = cleanNumericInput(this.value, true);

            if (oldValue !== cleaned) {
                this.value = cleaned;
                // Restore cursor position
                this.setSelectionRange(cursorPos - 1, cursorPos - 1);
            }
        });

        // Validate input in real-time
        input.addEventListener('keydown', function (e) {
            // Allow: backspace, delete, tab, escape, enter
            if ([8, 9, 27, 13, 46].indexOf(e.keyCode) !== -1 ||
                // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
                (e.keyCode === 65 && e.ctrlKey === true) ||
                (e.keyCode === 67 && e.ctrlKey === true) ||
                (e.keyCode === 86 && e.ctrlKey === true) ||
                (e.keyCode === 88 && e.ctrlKey === true) ||
                // Allow: home, end, left, right
                (e.keyCode >= 35 && e.keyCode <= 39)) {
                return;
            }

            // Ensure it's a number or decimal point
            if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) &&
                (e.keyCode < 96 || e.keyCode > 105) &&
                e.keyCode !== 190 && e.keyCode !== 110) {
                e.preventDefault();
            }

            // Prevent multiple decimal points
            if ((e.keyCode === 190 || e.keyCode === 110) && this.value.indexOf('.') !== -1) {
                e.preventDefault();
            }
        });

        // Handle paste events
        input.addEventListener('paste', function (e) {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const cleaned = cleanNumericInput(pastedText, true);
            this.value = cleaned;
        });

        // Initial formatting
        if (input.value) {
            input.value = formatNumber(parseFormattedNumber(input.value), 2);
        }
    });

    // Handle quantity inputs (integers only)
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        // Format on blur
        input.addEventListener('blur', function () {
            const cleaned = cleanNumericInput(this.value, false);
            if (cleaned === '') {
                this.value = '';
            } else {
                this.value = formatNumber(cleaned, 0);
            }
        });

        // Remove formatting on focus
        input.addEventListener('focus', function () {
            const cleaned = parseFormattedNumber(this.value);
            this.value = cleaned === '0' ? '' : cleaned;
            this.select();
        });

        // Clean input in real-time (prevent alphabets)
        input.addEventListener('input', function (e) {
            const cursorPos = this.selectionStart;
            const oldValue = this.value;
            const cleaned = cleanNumericInput(this.value, false);

            if (oldValue !== cleaned) {
                this.value = cleaned;
                // Restore cursor position
                this.setSelectionRange(cursorPos - 1, cursorPos - 1);
            }
        });

        // Validate input - integers only
        input.addEventListener('keydown', function (e) {
            // Allow: backspace, delete, tab, escape, enter
            if ([8, 9, 27, 13, 46].indexOf(e.keyCode) !== -1 ||
                // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
                (e.keyCode === 65 && e.ctrlKey === true) ||
                (e.keyCode === 67 && e.ctrlKey === true) ||
                (e.keyCode === 86 && e.ctrlKey === true) ||
                (e.keyCode === 88 && e.ctrlKey === true) ||
                // Allow: home, end, left, right
                (e.keyCode >= 35 && e.keyCode <= 39)) {
                return;
            }

            // Ensure it's a number only (no decimals)
            if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) &&
                (e.keyCode < 96 || e.keyCode > 105)) {
                e.preventDefault();
            }
        });

        // Handle paste events
        input.addEventListener('paste', function (e) {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const cleaned = cleanNumericInput(pastedText, false);
            this.value = cleaned;
        });

        // Initial formatting
        if (input.value) {
            input.value = formatNumber(parseFormattedNumber(input.value), 0);
        }
    });

    // Clean formatted values before form submission
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            // Remove formatting from all currency and quantity inputs
            this.querySelectorAll('.currency-input, .quantity-input').forEach(input => {
                input.value = parseFormattedNumber(input.value);
            });
        });
    });


    // Initialize Flatpickr date picker for dd/mm/yyyy format
    const dateInputs = document.querySelectorAll('input.date-input, input[placeholder*="dd/mm/yyyy"]');
    dateInputs.forEach(input => {
        flatpickr(input, {
            dateFormat: 'd/m/Y',
            altInput: true,
            altFormat: 'd/m/Y',
            allowInput: true,
            locale: {
                firstDayOfWeek: 1 // Monday
            }
        });
    });
});

// CSRF Token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
