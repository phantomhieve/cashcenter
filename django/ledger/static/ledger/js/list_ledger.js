document.addEventListener('DOMContentLoaded', ()=>{
    let url = new URL(window.location);
    let params = new URLSearchParams(url.search);
    let element = document.querySelector("#alert")
    document.querySelector('#id_l_r_date_0').value = params.get('l_r_date_min');
    document.querySelector('#id_l_r_date_1').value = params.get('l_r_date_max');
    
    // Alert for deleting content
    let element_delete = document.querySelector("#alert_delete");
    let content_delete = document.querySelector('#alert_delete_content');
    if(params.get('lr-no')){
        element_delete.style.display = "block";
        content_delete.innerHTML = `${params.get('lr-no')}`
    }
    else
        element_delete.style.display = "none";    


    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});

        