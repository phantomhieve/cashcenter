document.addEventListener('DOMContentLoaded', ()=>{
    
    let url = new URL(window.location);
    let params = new URLSearchParams(url.search);
    
    // Alert for wrong submission
    let element = document.querySelector("#alert_invalid")
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
    
    $('#myModal').on('shown.bs.modal', function () {
        $('#myInput').trigger('focus')
    })
});
