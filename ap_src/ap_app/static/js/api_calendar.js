var calendarClickToggle = true;
var token = document.currentScript.getAttribute("token");

//Send the data to the backend
function sendData(username, date, half_day, half_day_time, type) {
    var data = JSON.stringify({"username": username, "date": date, "half_day": half_day, "half_day_time": half_day_time, "type": type})
    if (type == "add") {
        var link = window.location.origin + "/absence/click_add"
    } else {
        var link = window.location.origin + "/absence/click_remove"
    }
    console.log(link)
    fetch(link, {
        method: "post",
        headers: {
            "X-CSRFToken": token
        },
        body: data
    })
    .then(() => {
        location.reload()
    })
    .catch(err => {
        console.log(err)
    })
}

//Clickable Calendar
document.addEventListener('click', function(e) {
    if (calendarClickToggle == true) {
        if (e.target.id.includes("/")) {
            var data = e.target.id.split("/"); var username = data[0]; var date = data[1]; var absent = data[2];
            //Add an absence
            if (absent == "FALSE") {
                //This is a half day
                if (e.shiftKey) {
                    document.getElementById("halfDayConfirmation").style.display = "block";
                    //Morning Clicked
                    document.getElementById("halfDayMorning").onclick = function() {
                        sendData(username, date, true, "M", "add")
                        document.getElementById("halfDayConfirmation").style.display = "none";
                    }
                    document.getElementById("halfDayAfternoon").onclick = function() {
                        sendData(username, date, true, "A", "add")
                        document.getElementById("halfDayConfirmation").style.display = "none";
                    }
                }
                //Full day absence
                else {
                    sendData(username, date, false, "N", "add")
                }
            }
            //Remove an absnece
            else {
                var confirmationPage = document.getElementById("confirmationBox")
                confirmationPage.style.display = "block";
                document.getElementById("removeAbsence").onclick = function() {
                    sendData(username, date, false, "N", "remove")
                    confirmationPage.style.display = "none";
                }
                document.getElementById("cancelAbsence").onclick = function() {
                    confirmationPage.style.display = "none";
                }
            }
        }
    }
}, false)

//Toggle clickable calendar on/off
var calendarClickButton = document.getElementById("ClickToggle")
calendarClickButton.onclick = function() {
    if (calendarClickToggle == false) {
        calendarClickButton.style.borderColor = "green";
        calendarClickToggle = true
    } else {
        calendarClickButton.style.borderColor = "red";
        calendarClickToggle = false
    }
}