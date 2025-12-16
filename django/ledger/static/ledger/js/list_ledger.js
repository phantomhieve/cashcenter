document.addEventListener('DOMContentLoaded', () => {
    let url = new URL(window.location);
    let params = new URLSearchParams(url.search);
    let element = document.querySelector("#alert")
    document.querySelector('#id_l_r_date_0').value = params.get('l_r_date_min');
    document.querySelector('#id_l_r_date_1').value = params.get('l_r_date_max');

    // Alert for deleting content
    let element_delete = document.querySelector("#alert_delete");
    let content_delete = document.querySelector('#alert_delete_content');
    if (params.get('lr-no')) {
        element_delete.style.display = "block";
        content_delete.innerHTML = `${params.get('lr-no')}`
    }
    else
        element_delete.style.display = "none";

    // Alert for update content
    let element_update = document.querySelector("#alert_update");
    let content_update = document.querySelector('#alert_update_content');
    if (params.get('update')) {
        element_update.style.display = "block";
        content_update.innerHTML = `${params.get('update')}`
    }
    else
        element_update.style.display = "none";


    $(".clickable-row").click(function () {
        window.location = $(this).data("href");
    });

    // Date Input Placeholder Color Logic
    const updateDateColor = (input) => {
        input.style.color = input.value ? '#1f2937' : '#9ca3af';
    };

    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        updateDateColor(input);
        ['change', 'input'].forEach(event =>
            input.addEventListener(event, () => updateDateColor(input))
        );
    });

    // ---------------------------------------------------------
    // Refactored Logic moved from list_ledger.html
    // ---------------------------------------------------------

    // Filter toggle icon animation
    $('#collapseButton').on('click', function () {
        $(this).find('.filter-icon').toggleClass('fa-chevron-down fa-chevron-up');
    });

    // Clear filter form function - attached to window to be accessible if called inline (onclick="clearFilterForm()")
    window.clearFilterForm = function () { // Expose to global scope for onclick handler
        document.getElementById('filterForm').reset();
        $('.filter-input-chip').val('');
        $('.filter-select-chip').val('').trigger('change');
        updateSelectColors();
    }

    // Update select colors based on selection
    function updateSelectColors() {
        $('.filter-select-chip').each(function () {
            const $select = $(this);
            const section = $select.data('section');
            const value = $select.val();

            // Remove all color classes
            $select.removeClass('filter-selected-status filter-selected-delivery filter-selected-columns filter-selected-mode');

            // Add appropriate color class based on section and value
            if (value && value !== '') {
                if (section === 'status') {
                    $select.addClass('filter-selected-status');
                } else if (section === 'mode') {
                    $select.addClass('filter-selected-mode');
                }
            }
        });
    }

    updateSelectColors();
    $('.filter-select-chip').on('change', function () {
        updateSelectColors();
    });

    // Handle input focus/blur for labels
    $('.filter-input-chip').on('focus', function () {
        $(this).siblings('.filter-floating-label').addClass('label-focused');
    }).on('blur', function () {
        $(this).siblings('.filter-floating-label').removeClass('label-focused');
        if ($(this).val() && $(this).val() !== '') {
            $(this).siblings('.filter-floating-label').addClass('label-active');
        } else {
            $(this).siblings('.filter-floating-label').removeClass('label-active');
        }
    });

    // Financial Password Auth Logic
    $('#trigger-financial-auth').on('click', function () {
        // Use global function from financial_modal.js
        if (typeof openFinancialCheck === 'function') {
            openFinancialCheck(function () {
                // Success callback
                $('#secure-total-display').hide();
                $('#trigger-financial-auth').hide();
                $('#actual-total-value').fadeIn();
            });
        } else {
            console.error('Global financial check function not found');
        }
    });

    // AutoComplete Logic
    // Only init if element exists and data attributes are present
    const $autoComplete = $('.lrAutoComplete');
    if ($autoComplete.length > 0) {
        const autocompleteUrl = $autoComplete.data('url');
        const redirectBaseUrl = $autoComplete.data('redirect-url');
        const queryParams = $autoComplete.data('query-params'); // e.g. "&other=param"

        if (autocompleteUrl) {
            $autoComplete.autoComplete({
                minLength: 1,
                resolverSettings: {
                    url: autocompleteUrl,
                    requestThrottling: 700
                },
            });

            $autoComplete.on('autocomplete.select', (evt, item) => {
                if (redirectBaseUrl) {
                    window.location.replace(`${redirectBaseUrl}${item}${queryParams || ''}`);
                }
            });
        }
    }
});
