/*Logic for spinner for create team button */
document.addEventListener('DOMContentLoaded', function() {
    var nameInput = document.getElementById('nameInput');
    var descriptionInput = document.getElementById('id_description');
    var submitButton = document.getElementById('submit');
    var labelButton = document.getElementById('label_button');

    function updateButtonState() {
        const nameValue = nameInput.value.trim();
        const descriptionValue = descriptionInput.value.trim();
        const shouldEnable = nameValue !== "" && descriptionValue !== "";

        if (shouldEnable) {
            submitButton.removeAttribute("disabled");
            labelButton.removeAttribute("disabled");
        } else {
            submitButton.setAttribute("disabled", true);
            labelButton.setAttribute("disabled", true);
        }
    }

    nameInput.addEventListener("keyup", updateButtonState);
    descriptionInput.addEventListener("keyup", updateButtonState);

    labelButton.addEventListener('click', () => {
        if (!labelButton.hasAttribute("disabled")) {
            labelButton.classList.add('is-loading');
            labelButton.setAttribute('disabled', true);
        }
    });
});

/*Function will add spinner to button element, input element will not work */
/*Main use is buttons with no required entry field - Use above example otherwise */
function add_spinner_to_button(button_class_name) {
    document.addEventListener('DOMContentLoaded', function() {
        var buttons = document.querySelectorAll(button_class_name);
        /* Must loop through all occurrences of button is-success as querySelector only targets the first occurrence */
        buttons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                button.classList.add("is-loading");
            });
        });
    });
}

/* Re-use these naming conventions for elements where they apply, for consistency */
add_spinner_to_button('.join-team-button');
add_spinner_to_button('.leave-team-button');
add_spinner_to_button('.edit-team-button');
add_spinner_to_button('.settings-submit-button');
add_spinner_to_button('.view-team-button');
add_spinner_to_button('.refresh-calendar-button');