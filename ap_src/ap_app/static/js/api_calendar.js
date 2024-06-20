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
            console.log(data)
            //Add an absence
            if (absent == "FALSE") {
                //This is a half day
                if (e.shiftKey) {
                    fetch("calendar/check_permissions", {
                        method: "post",
                        headers: {
                            "X-CSRFToken": token
                        },
                        body: data
                    })
                    .then(() => {
                        location.reload()
                    })
                    var confirmationPage = document.getElementById("half")

                    // {% check_permissions member request.user as editable %}
                    //         {% if editable %}
                    //         <td>{{member.user.username}}*</td>
                    //         {% else %}
                    //         <td>{{member.user.username}}</td>
                    //         {% endif %}

                    confirmationPage.classList.add("is-active")
                    //Morning Clicked
                    document.getElementById("morningBTN").onclick = function() {
                        sendData(username, date, true, "M", "add", "E")
                        confirmationPage.classList.remove("is-active")
                    }
                    document.getElementById("afternoonBTN").onclick = function() {
                        sendData(username, date, true, "A", "add", "E")
                        confirmationPage.classList.remove("is-active")
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
                var confirmationPage = document.getElementById("remove")
                confirmationPage.classList.add("is-active")
                document.getElementById("removeBTN").onclick = function() {
                    sendData(username, date, false, "N", "remove", absence_type)
                    confirmationPage.classList.remove("is-active")
                }
            }
        }
    }
}, false)

//Toggle clickable calendar on/off
var calendarClickButton = document.getElementById("CalendarClick-Toggle")
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
        if (!calendarID.toUpperCase().includes(input.value.toString().toUpperCase())) {
            calendars[cal].style.display = "none";
        } else {
            calendars[cal].style.display = "";
        }
    }
}

function sortTeams(e) {
    var url = new URL(window.location.href)
    url.searchParams.set("sortBy", e.value)

    window.location.replace(url)
}

function setDate(e, id) {
    data = e.value.split(" ")
    month = data[0]
    year = data[1]
    if (id == 0) {
        window.location.replace(window.location.origin + `/calendar/${month}/${year}`)
    } else {
        window.location.replace(window.location.origin + `/teams/api-calendar/${id}/${month}/${year}`)
    }
}

function openModal(id) {
    document.getElementById(id).classList.add("is-active");
}

function closeModal(id) {
    document.getElementById(id).classList.remove("is-active")
}

window.onclick = function(event) {
    if (event.target.id == 'modalBackground') {
        var modalId = event.target.dataset.modalId;
        document.getElementById(modalId).classList.remove("is-active")
    }
}