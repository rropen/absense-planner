var calendarClickToggle = true;
var token = document.currentScript.getAttribute("token");

//Send the data to the backend
function sendData(username, date, half_day, half_day_time, type, absence_type) {
    var data = JSON.stringify({"username": username, "date": date, "half_day": half_day, "half_day_time": half_day_time, "type": type, "absence_type": absence_type})
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
                        sendData(username, date, true, "M", "add", "E")
                        document.getElementById("halfDayConfirmation").style.display = "none";
                    }
                    document.getElementById("halfDayAfternoon").onclick = function() {
                        sendData(username, date, true, "A", "add", "E")
                        document.getElementById("halfDayConfirmation").style.display = "none";
                    }
                    document.getElementById("halfDayClose").onclick = function() {
                        document.getElementById("halfDayConfirmation").style.display = "none";
                    }
                }
                //Full day absence
                else {
                    sendData(username, date, false, "N", "add", "E")
                }
            }
            //Remove an absnece
            else {
                var absence_type = e.target.dataset.absenceType;
                var confirmationPage = document.getElementById("confirmationBox")
                confirmationPage.style.display = "block";
                document.getElementById("cancelAbsece").onclick = function() {
                    document.getElementById("confirmationBox").style.display = "none";
                }
                document.getElementById("absenceClose").onclick = function() {
                    document.getElementById("confirmationBox").style.display = "none";
                }
                document.getElementById("removeAbsence").onclick = function() {
                    sendData(username, date, false, "N", "remove", absence_type)
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

function closeElement(e) {
    e.style.display = "none";
}

//Team filter
function filterTeams(input) {
    var calendars = Array.from(document.getElementById("calendar-group").children)
    for (cal in calendars) {
        var calendarID = calendars[cal].id.toString()
        calendarID = calendarID.replace("title-", "")
        console.log(calendarID)
        if (!calendarID.toUpperCase().includes(input.value.toString().toUpperCase())) {
            calendars[cal].style.display = "none";
        } else {
            calendars[cal].style.display = "";
        }
    }
}