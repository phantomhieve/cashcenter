/**
 * Universal Financial Modal Handler
 * Extracted from navbar.html
 */

// Callback storage
var onAuthSuccess = null;

function getFinancialElements() {
    return {
        modal: $('#universalFinancialModal'),
        form: $('#universalFinancialForm'),
        input: $('#fyPassword'),
        title: $('#universalFinancialModalLabel'),
        msg: $('#universalModalMessage'),
        btn: $('#universalSubmitBtn'),
        mode: $('#universalModalMode'),
        error: $('#universalError')
    };
}

function openFyModal(yearId, yearName) {
    var el = getFinancialElements();
    
    // Reset to Switch Year Mode
    el.mode.val('switch_year');
    el.form.off('submit').on('submit', function() { return true; }); // Default submit
    el.title.text('Switch Financial Year');
    el.msg.html('Enter password to switch to <b>' + yearName + '</b>');
    el.btn.text('Switch Year');
    
    $('#fyTargetInput').val(yearId);
    el.input.val('').removeClass('is-invalid');
    el.modal.modal('show');
    setTimeout(function() { el.input.focus(); }, 500);
}

function openFinancialCheck(callback) {
    var el = getFinancialElements();
    
    // Validation Mode
    el.mode.val('validate');
    onAuthSuccess = callback;
    
    el.title.text('Security Check');
    el.msg.text('Enter Financial Password to reveal content');
    el.btn.text('Unlock');
    
    el.input.val('').removeClass('is-invalid');
    el.modal.modal('show');
    setTimeout(function() { el.input.focus(); }, 500);

    // Handle AJAX submit
    el.form.off('submit').on('submit', function(e) {
        e.preventDefault();
        var password = el.input.val();
        // Get URL from data attribute on the form
        var verifyUrl = el.form.data('verify-url'); 
        
        if (!verifyUrl) {
            console.error('Verify URL not found on form data-verify-url attribute');
            el.error.text('Configuration Error: Missing URL');
            return;
        }

        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // UI Loading
        el.btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Checking...');
        el.input.removeClass('is-invalid');

        fetch(verifyUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ password: password })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            el.btn.prop('disabled', false).text('Unlock');
            
            if (data.success) {
                el.modal.modal('hide');
                if (onAuthSuccess) onAuthSuccess();
            } else {
                el.input.addClass('is-invalid');
                el.error.text(data.message || 'Incorrect Password');
            }
        })
        .catch(function(err) {
            console.error(err);
            el.btn.prop('disabled', false).text('Unlock');
            el.input.addClass('is-invalid');
            el.error.text('Error verifying password');
        });
    });
}
