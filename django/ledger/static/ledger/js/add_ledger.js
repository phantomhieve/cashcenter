document.addEventListener('DOMContentLoaded', ()=>{
    // Alert for wrong submission
    let url = new URL(window.location);
    let params = new URLSearchParams(url.search);
    let element = document.querySelector("#alert_lr")
    if(params.get('invalid'))
        element.style.display = "block";
    else
        element.style.display = "none";
    $('#myModal').on('shown.bs.modal', function () {
        $('#myInput').trigger('focus')
    })

    // Alert for adding/updating content
    let element_add = document.querySelector("#alert_add");
    let content_add = document.querySelector('#alert_add_content');
    if(params.get('sucessful')){
        element_add.style.display = "block";
        content_add.innerHTML = `${params.get('sucessful')}`
    }
    else
        element_add.style.display = "none";

    // Fixing decimal value
    function fixDecimalValue(event){
        this.value = parseFloat(this.value).toFixed(2);
    }
    document.getElementById('id_frieght').onchange = fixDecimalValue(event);
    document.getElementById('id_bill_ammount').onchange = fixDecimalValue(event);
});
