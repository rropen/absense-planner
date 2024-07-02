/*Logic for spinner for create team button -KJ*/
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("nameInput").addEventListener("keyup", function() {
        document.getElementById("id_description").addEventListener("keyup", function() {
        var nameInput = document.getElementById('nameInput').value;
        var descriptionInput = document.getElementById('id_description').value;
        if (nameInput !="" && descriptionInput !="")  {
            document.getElementById('submit').removeAttribute("disabled");
            document.getElementById('label_button').removeAttribute("disabled");
        } else {
            document.getElementById('submit').setAttribute("disabled", null);
            document.getElementById('label_button').setAttribute("disabled", null);
        }
    const label_button = document.getElementById('label_button');
    if(document.getElementById('label_button').getAttribute("disabled") ==true
    && document.getElementById('submit').getAttribute("disabled")==true);
	label_button.addEventListener('click', () => {
		label_button.classList.add('is-loading');
        label_button.setAttribute('disabled', true);
	});
})});
});

/*Function will add spinner to buttons, inputs will not work -KJ */
function add_spinner_to_button(button_class_name) {
    document.addEventListener('DOMContentLoaded', function() {
        var buttons = document.querySelectorAll(button_class_name);
        /* Must loop through all occurrences of button is-success as querySelector only targets the first occurrence -KJ */
        buttons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                button.classList.add("is-loading");
            });
        });
    });
}

add_spinner_to_button('.button.is-success'); /*Join Team Button -KJ */
add_spinner_to_button('.button.is-danger'); /*Leave Team Button -KJ */
add_spinner_to_button('.button.is-info'); /*Edit Button -KJ */
add_spinner_to_button('.button.is-fullwidth.is-info'); /*Update Button -KJ */
add_spinner_to_button('.button.is-link'); /*View Team Button -KJ */
add_spinner_to_button('.mr-4.button'); /*Refresh Calendar Button -KJ */