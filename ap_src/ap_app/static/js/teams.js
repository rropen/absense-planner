function openLeaveTeamModal(teamId, teamName, userRole, memberCount, membersJson) {
    const leaveModal = document.getElementById('leaveTeamModal');
    const deleteModal = document.getElementById('deleteTeamModal');
    const transferModal = document.getElementById('transferOwnershipModal');

    document.getElementById('leaveTeamName').innerText = teamName;
    document.getElementById('deleteTeamName').innerText = teamName;

    $('#leaveTeamInput').val(teamId);
    $('#deleteTeamInput').val(teamId);

    const members = JSON.parse(membersJson || '[]');
    const otherMembers = members.filter(m => !m.is_self);
    const isOwner = userRole === 'Owner';

    if (isOwner && memberCount === 1) {
        // Only member = show delete modal
        deleteModal.classList.add('is-active');

        document.getElementById('cancelDeleteButton').onclick = () => {
            deleteModal.classList.remove('is-active');
        };
        document.querySelector('#deleteTeamModal .modal-close').onclick = () => {
            deleteModal.classList.remove('is-active');
        };

    } else if (isOwner && otherMembers.length > 0) {
        // Owner with other members = show transfer modal
        document.getElementById('transfer-team-name').innerText = teamName;
        document.getElementById('transfer-team-id').value = teamId;

        const select = document.getElementById('new-owner-select');
        select.innerHTML = '';

        otherMembers.forEach(member => {
            const option = document.createElement('option');
            option.value = member.username;
            option.textContent = `${member.full_name} (${member.username})`;
            select.appendChild(option);
        });

        transferModal.classList.add('is-active');

        document.getElementById('cancelTransferButton').onclick = () => {
            transferModal.classList.remove('is-active');
        };
        document.querySelector('#transferOwnershipModal .modal-close').onclick = () => {
            transferModal.classList.remove('is-active');
        };

    } else {
        // Leave modal
        leaveModal.classList.add('is-active');

        document.getElementById('cancelLeaveButton').onclick = () => {
            leaveModal.classList.remove('is-active');
        };
        document.querySelector('#leaveTeamModal .modal-close').onclick = () => {
            leaveModal.classList.remove('is-active');
        };
    }
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

function openDeleteTeamModal(button) {
    const modal = document.getElementById('deleteTeamModal');
    const cancelButton = document.getElementById('cancelDeleteButton');
    const modalCloseButton = document.querySelector('#deleteTeamModal .modal-close');

    modal.classList.add('is-active');

    cancelButton.onclick = () => {
        modal.classList.remove('is-active');
    };

    modalCloseButton.onclick = () => {
        modal.classList.remove('is-active');
    };
}