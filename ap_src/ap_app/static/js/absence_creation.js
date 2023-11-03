var calendar = document.getElementById("id_start_date");
calendar.addEventListener("change", function(e){
    document.getElementById("id_end_date").value = calendar.value
})