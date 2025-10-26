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

    // Change floating point
    function fixDecimalValueInit(id){
        element = document.getElementById(id);
        if(element.value){
            element.value = parseFloat(element.value).toFixed(2)
        }
    }

    fixDecimalValueInit('id_frieght');
    fixDecimalValueInit('id_bill_ammount');

    // Change floating point pcs/mtr
    element = document.getElementById('id_pcs_mtr');
    if(element.value!="" && Number(element.value)==element.value){
        element.value = Number(element.value);
    }

    document.getElementById('id_frieght').onchange = function (event){
        this.value = parseFloat(this.value).toFixed(2);
    }

    // Adding numbers delimeter "+", " "
    function addSpace(valueString){
        let total = 0;
        let splitArray = valueString.split(" ");
        if(valueString.includes("+"))
            splitArray = valueString.split("+");
        else if(splitArray.length===1)
            splitArray = [valueString];
        splitArray.forEach((value)=>{
            if(value!=="")
                total+=parseFloat(value)
        })
        return total;
    }

    // Addable fields modify
    document.getElementById('id_bill_ammount').onchange = function (event){
        this.value = addSpace(this.value);
        this.value = parseFloat(this.value).toFixed(2);
    }

    document.getElementById('id_pcs_mtr').onchange = function (event){
        this.value = addSpace(this.value);
        this.value = parseFloat(this.value).toFixed(2);
    }

});
