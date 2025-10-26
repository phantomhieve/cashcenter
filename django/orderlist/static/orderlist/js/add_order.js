document.addEventListener('DOMContentLoaded', ()=>{
	
	// Alert for wrong submission
	let url = new URL(window.location);
	let params = new URLSearchParams(url.search);
	let element = document.querySelector("#alert_lr")
	if(params.get('invalid'))
		element.style.display = "block";
	else
		element.style.display = "none";

	// Alert for adding/updating content
	let element_add = document.querySelector("#alert_add");
	let content_add = document.querySelector('#alert_add_content');
	if(params.get('sucessful')){
		element_add.style.display = "block";
		content_add.innerHTML = `${params.get('sucessful')}`
	}
	else if(params.get('update')){
		element_add.style.display = "block";
		content_add.innerHTML = `${params.get('update')}`
	}
	else
		element_add.style.display = "none";

	// Dynamic inline formset row add
	// Deletion via trash icon with confirm modal
	const fulfillmentTableBody = document.getElementById('fulfillment-rows');
	function attachImmediateDelete(container){
		container.querySelectorAll('button.delete-fulfillment').forEach((btn)=>{
			btn.addEventListener('click', (e)=>{
				e.preventDefault();
				const row = btn.closest('tr.fulfillment-row');
				const checkbox = row.querySelector('input.fulfillment-delete-input');
				if(checkbox){
					checkbox.checked = true;
					const form = checkbox.closest('form');
					if(form){ form.submit(); }
				}
			});
		});
	}

	if(fulfillmentTableBody){
		attachImmediateDelete(fulfillmentTableBody);
	}

	// Show/hide agent name field based on mode selection
	function initAgentNameToggle() {
		const modeField = document.getElementById('id_mode');
		const agentNameField = document.getElementById('id_agent_name');
		const agentNameGroup = document.getElementById('agent-name-group');

		if (!modeField || !agentNameGroup) {
			return;
		}

		function toggleAgentNameField() {
			if (modeField.value === 'agent') {
				agentNameGroup.style.display = 'block';
				agentNameGroup.style.visibility = 'visible';
				if (agentNameField) {
					agentNameField.required = true;
				}
			} else {
				agentNameGroup.style.display = 'none';
				agentNameGroup.style.visibility = 'hidden';
				if (agentNameField) {
					agentNameField.required = false;
					agentNameField.value = '';
				}
			}
		}

		// Add event listener
		modeField.addEventListener('change', toggleAgentNameField);
		
		// Initial check
		toggleAgentNameField();
	}

	// Initialize the agent name toggle immediately
	initAgentNameToggle();

	// Validation: Check if total fulfillment quantity exceeds number of parcels
	function validateFulfillmentQuantity() {
		const numParcelsField = document.getElementById('id_num_parcels');
		
		if (!numParcelsField) {
			return true;
		}

		const numParcels = parseInt(numParcelsField.value) || 0;
		let totalQuantity = 0;

		// Get all number inputs in the fulfillment table
		const fulfillmentTable = document.getElementById('fulfillment-rows');
		if (!fulfillmentTable) {
			return true;
		}

		const allNumberInputs = fulfillmentTable.querySelectorAll('input[type="number"]');

		allNumberInputs.forEach((input) => {
			// Check if this row is marked for deletion
			const row = input.closest('tr.fulfillment-row');
			const deleteCheckbox = row ? row.querySelector('input[name$="-DELETE"]') : null;
			
			if (deleteCheckbox && deleteCheckbox.checked) {
				return; // Skip deleted rows
			}
			
			if (input.value && !isNaN(parseInt(input.value))) {
				const quantity = parseInt(input.value);
				totalQuantity += quantity;
			}
		});

		if (totalQuantity > numParcels) {
			showValidationError(`Wrong input: Total fulfillments (${totalQuantity}) exceeds number of parcels (${numParcels}).`);
			return false;
		}

		return true;
	}

	// Function to show validation error notification
	function showValidationError(message) {
		// Remove any existing validation error
		const existingError = document.getElementById('validation-error');
		if (existingError) {
			existingError.remove();
		}

		// Create new error notification container
		const errorContainer = document.createElement('div');
		errorContainer.id = 'validation-error';
		errorContainer.className = 'container';
		errorContainer.innerHTML = `
			<div class="alert alert-danger alert-dismissible fade show" role="alert">
				<strong>Validation Error:</strong> ${message}
				<button type="button" class="close" data-dismiss="alert" aria-label="Close">
					<span aria-hidden="true">&times;</span>
				</button>
			</div>
		`;

		// Insert at the top of the body content, before the form container
		const formContainer = document.querySelector('.container.order-form');
		if (formContainer) {
			formContainer.parentNode.insertBefore(errorContainer, formContainer);
		}
	}

	// Make validation function globally available
	window.validateFulfillmentQuantity = validateFulfillmentQuantity;
	
	// Add form submission validation with delay to ensure DOM is ready
	setTimeout(function() {
		const form = document.querySelector('form');
		
		if (form) {
			form.addEventListener('submit', function(e) {
				// Force validation before any submission
				const isValid = validateFulfillmentQuantity();
				
				if (!isValid) {
					e.preventDefault();
					e.stopPropagation();
					e.stopImmediatePropagation();
					return false;
				}
			});
		}
	}, 100);

	// Add real-time validation on quantity field changes
	function addRealTimeValidation() {
		const fulfillmentRows = document.querySelectorAll('tr.fulfillment-row');
		fulfillmentRows.forEach(row => {
			const quantityField = row.querySelector('input[name*="quantity"]') || 
								 row.querySelector('input[type="number"]');
			if (quantityField) {
				quantityField.addEventListener('input', function() {
					// Remove any existing validation error when user starts typing
					const existingError = document.getElementById('validation-error');
					if (existingError) {
						existingError.remove();
					}
				});
			}
		});
	}

	// Initialize real-time validation
	addRealTimeValidation();
});
