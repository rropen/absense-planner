var apiURL = document.currentScript.getAttribute("apiURL");

function openLeaveTeamModal(teamId) {
    const modal = document.getElementById('leaveTeamModal');
    const confirmButton = $("#confirmLeaveButton");
    const cancelButton = document.getElementById('cancelLeaveButton');
    const modalCloseButton = document.querySelector('#leaveTeamModal .modal-close');

    // Find hidden input used to send selected Team ID.
    const teamIdInputElement = confirmButton.parent().children("[name='team_id']").eq(0)

    modal.classList.add('is-active');

    // Add the current Team ID to the form so it can be sent in the request when the confirm button is pressed.
    teamIdInputElement.val(teamId);

    cancelButton.addEventListener('click', () => {
        modal.classList.remove('is-active');
        teamIdInputElement.val(""); // Reset Team ID input
    });

    modalCloseButton.addEventListener('click', () => {
        modal.classList.remove('is-active');
        teamIdInputElement.val("");
    });
}

function showSuccessModal() {
    const successModal = document.getElementById('successModal');
    const closeSuccessButton = document.getElementById('closeSuccessButton');

    successModal.classList.add('is-active');
    var teamName = sessionStorage.getItem('teamName')

    var successModalMessage = document.getElementById("success-modal-team-message");
    successModalMessage.innerHTML = "You have successfully left " + teamName;

    closeSuccessButton.addEventListener('click', () => {
        successModal.classList.remove('is-active');
    });
}

// Check sessionStorage on page load to show success modal if necessary
window.addEventListener('load', () => {
    if (sessionStorage.getItem('showSuccessModal') === 'true') {
        sessionStorage.removeItem('showSuccessModal'); // Clear the flag
        showSuccessModal(); // Show the success modal
    }
});

function JoinTeam(e, user, redirect) {
    var data = JSON.stringify({"username": user, "team": e.id})
    fetch(apiURL + 'manage/?method=join', {
        method: "post",
        body: data,
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(() => {
        if (redirect) {
            location.replace(location.origin + "/teams/join")
        } else {
            location.reload()
        }
    })
    .catch(err => {
        console.log(err)
    })
}

function starHover(element) {
    if (element.dataset.star == 'False'){
        let starElement = $(element).children(".fa-star");
        starElement.removeClass("far")
        starElement.addClass("fas")
        element.dataset.star = 'True'
    }
}

function removeHover(element) {
    if (element.dataset.star == 'True'){
        let starElement = $(element).children(".fa-star");
        starElement.removeClass("fas")
        starElement.addClass("far")
        element.dataset.star = 'False'
    }
}

function openDeleteTeamModal(button) {
    const teamId = button.id;
    const modal = document.getElementById('deleteTeamModal');
    const confirmButton = document.getElementById('confirmDeleteButton');
    const cancelButton = document.getElementById('cancelDeleteButton');
    const modalCloseButton = document.querySelector('#deleteTeamModal .modal-close');

    modal.classList.add('is-active');

    confirmButton.onclick = () => {
        DeleteTeam(parseInt(teamId));
        modal.classList.remove('is-active');
    };

    cancelButton.onclick = () => {
        modal.classList.remove('is-active');
    };

    modalCloseButton.onclick = () => {
        modal.classList.remove('is-active');
    };
}

function DeleteTeam(teamId) {
    var data = JSON.stringify({ "id": teamId });

    fetch(apiURL + 'teams/?method=delete&format=json', {
        method: "POST",
        body: data,
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(() => {
        location.replace(location.origin + "/teams");
    })
    .catch(err => {
        console.log(err);
    });
}