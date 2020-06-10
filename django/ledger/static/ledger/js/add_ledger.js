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

    document.getElementById('id_frieght').onchange = function(event){
        this.value = parseFloat(this.value).toFixed(2);
    }

    document.getElementById('id_price').onchange = function(event){
        this.value = parseFloat(this.value).toFixed(2);
    }
});
