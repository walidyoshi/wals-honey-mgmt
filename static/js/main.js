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
            const price = parseFloat(unitPriceInput.value) || 0;
            const qty = parseFloat(quantityInput.value) || 0;
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

    // Handle number inputs - remove leading zero on focus
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        // On focus, select all text so typing replaces it
        input.addEventListener('focus', function () {
            if (this.value === '0' || this.value === '') {
                this.select();
            }
        });

        // On blur, restore 0 if empty
        input.addEventListener('blur', function () {
            if (this.value === '' || this.value === null) {
                this.value = '0';
            }
        });

        // Prevent non-numeric characters
        input.addEventListener('keypress', function (e) {
            const char = String.fromCharCode(e.which);
            if (!/[0-9.]/.test(char)) {
                e.preventDefault();
            }
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
