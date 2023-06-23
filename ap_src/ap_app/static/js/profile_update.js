function addUserPermission(token) {
    var addValue = document.getElementById("user_permission_input").value;
    var data = JSON.stringify({"username": addValue})
    fetch("settings/add-user", {
        method: "post",
        headers: {
            "X-CSRFToken": token
        },
        body: data
    })
}

function deleteInputtedValue(element) {
    document.getElementById(element).value = "";
}