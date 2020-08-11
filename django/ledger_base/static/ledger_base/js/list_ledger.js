document.addEventListener('DOMContentLoaded', ()=>{
    let url = new URL(window.location);
    let params = new URLSearchParams(url.search);

    // Alert for deleting content
    let element_delete = document.querySelector("#alert_delete");
    let content_delete = document.querySelector('#alert_delete_content');
    if(params.get('lr-no')){
        element_delete.style.display = "block";
        content_delete.innerHTML = `${params.get('lr-no')}`
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
    
    //Alert for Approve content
    let element_approve = document.querySelector("#alert_approve");
    let content_approve = document.querySelector('#alert_approve_content');
    if(params.get('approve')){
        element_approve.style.display = "block";
        content_approve.innerHTML = `${params.get('approve')}`
    }
    else
        element_approve.style.display = "none";
})