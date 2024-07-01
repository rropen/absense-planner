var calendarClickToggle = true;
var token = document.currentScript.getAttribute("token");


/* Display the spinner while webpage is being refreshed -KJ*/
// document.addEventListener('DOMContentLoaded', function() {
//     const loader = document.querySelector('.loader');
//     window.addEventListener('load', function() {
//       loader.classList.add('loader--hidden');
//     });

//     window.addEventListener('beforeunload', function() {
//       loader.classList.remove('loader--hidden');
//     });
//   });

/* Display the spinner on a button while webpage is being refreshed -KJ */
/*DOM - Document Object Model must be loaded before */

//     document.getElementById('submit').addEventListener('click', function() {
//         var element = document.getElementById("submit")
//         console.log(element);
//         element.classList.add("block");
//         element.classList.add("is-loading");
//         var btnProcess = document.querySelector('.btn-process');
//         btnProcess.disabled = true;
//         btnProcess.value = 'disabled';
        
//         setTimeout(function() {
//             document.querySelector('.btn-ring').style.display = 'none';
//             btnProcess.disabled = false;
//             btnProcess.value = 'enabled'; // Reset the button value if needed
//         }, 3000);
//     });
// });

/*Logic to run loading animation for spinner button on create team page -KJ*/
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("nameInput").addEventListener("keyup", function() {
        document.getElementById("id_description").addEventListener("keyup", function() {
        var nameInput = document.getElementById('nameInput').value;
        var descriptionInput = document.getElementById('id_description').value;
        if (nameInput !="" && descriptionInput !="")  {
            document.getElementById('submit').removeAttribute("disabled");
            document.getElementById('button1').removeAttribute("disabled");
        } else {
            document.getElementById('submit').setAttribute("disabled", null);
            document.getElementById('button1').setAttribute("disabled", null);
        }
    const button1 = document.getElementById('button1');
    if(document.getElementById('button1').getAttribute("disabled") ==true
    && document.getElementById('submit').getAttribute("disabled")==true);
	button1.addEventListener('click', () => {
		button1.classList.add('is-loading');
    button1.setAttribute('disabled', true);
	});
})});
});

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
    if (calendarClickToggle == true && e.target.dataset.editable == "True") {
        if (e.target.id.includes("/")) {
            var data = e.target.id.split("/"); var username = data[0]; var date = data[1]; var absent = data[2];
            //Add an absence
            if (absent == "FALSE") {
                //This is a half day
                if (e.shiftKey) {
                    var confirmationPage = document.getElementById("half")
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