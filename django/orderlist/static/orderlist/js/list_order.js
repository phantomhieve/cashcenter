document.addEventListener('DOMContentLoaded', ()=>{
	let url = new URL(window.location);
	let params = new URLSearchParams(url.search);
	// Alert for deleting content
	let element_delete = document.querySelector("#alert_delete");
	let content_delete = document.querySelector('#alert_delete_content');
	if(params.get('order-no')){
		element_delete.style.display = "block";
		content_delete.innerHTML = `${params.get('order-no')}`
	}
	else
		element_delete.style.display = "none";

	// Alert for update content
	let element_update = document.querySelector("#alert_update");
	let content_update = document.querySelector('#alert_update_content');
	if(params.get('update')){
		element_update.style.display = "block";
		content_update.innerHTML = `${params.get('update')}`
	}
	else
		element_update.style.display = "none";

	$(".clickable-row").click(function() {
		window.location = $(this).data("href");
	});
});
