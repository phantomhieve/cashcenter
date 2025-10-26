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
});
