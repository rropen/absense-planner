function openLeaveTeamModal(teamId, teamName, userRole, memberCount) {
  const leaveModal = document.getElementById("leaveTeamModal");
  const deleteModal = document.getElementById("deleteTeamModal");

  document.getElementById("leaveTeamName").innerText = teamName;
  document.getElementById("deleteTeamName").innerText = teamName;

  $("#leaveTeamInput").val(teamId);
  $("#deleteTeamInput").val(teamId);

  if (userRole === "Owner" && memberCount === 1) {
    // Delete modal for when only member is owener
    deleteModal.classList.add("is-active");

    document.getElementById("cancelDeleteButton").onclick = () => {
      deleteModal.classList.remove("is-active");
    };
    document.querySelector("#deleteTeamModal .modal-close").onclick = () => {
      deleteModal.classList.remove("is-active");
    };
  } else {
    // Leave modal if not the only member
    leaveModal.classList.add("is-active");

    document.getElementById("cancelLeaveButton").onclick = () => {
      leaveModal.classList.remove("is-active");
    };
    document.querySelector("#leaveTeamModal .modal-close").onclick = () => {
      leaveModal.classList.remove("is-active");
    };
  }
}

function showSuccessModal() {
  const successModal = document.getElementById("successModal");
  const closeSuccessButton = document.getElementById("closeSuccessButton");

  successModal.classList.add("is-active");
  var teamName = sessionStorage.getItem("teamName");

  var successModalMessage = document.getElementById(
    "success-modal-team-message"
  );
  successModalMessage.innerHTML = "You have successfully left " + teamName;

  closeSuccessButton.addEventListener("click", () => {
    successModal.classList.remove("is-active");
  });
}

// Check sessionStorage on page load to show success modal if necessary
window.addEventListener("load", () => {
  if (sessionStorage.getItem("showSuccessModal") === "true") {
    sessionStorage.removeItem("showSuccessModal"); // Clear the flag
    showSuccessModal(); // Show the success modal
  }
});

function openDeleteTeamModal(button) {
  const modal = document.getElementById("deleteTeamModal");
  const cancelButton = document.getElementById("cancelDeleteButton");
  const modalCloseButton = document.querySelector(
    "#deleteTeamModal .modal-close"
  );

  modal.classList.add("is-active");

  cancelButton.onclick = () => {
    modal.classList.remove("is-active");
  };

  modalCloseButton.onclick = () => {
    modal.classList.remove("is-active");
  };
}
