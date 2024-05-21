var apiURL = document.currentScript.getAttribute("apiURL");

function JoinTeam(e, user, redirect) {
    var data = JSON.stringify({"username": user, "team": e.id})
    fetch(apiURL + 'api/manage/?method=join', {
        method: "post",
        body: data,
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(() => {
        if (redirect) {
            location.replace(location.origin + "/teams/api-calendar/" + e.id)
        } else {
            location.reload()
        }
    })
    .catch(err => {
        console.log(err)
    })
}

function starHover(e) {
    if (e.dataset.star == 'false'){
        e.innerHTML="<i class='fas fa-star'></i>"
        e.dataset.star = 'true'

    }
}

function removeHover(e) {
    if (e.dataset.star == 'true'){
        e.innerHTML="<i class='far fa-star'></i>"
        e.dataset.star = 'false'
    }
}

function favouriteTeam(e, user, id) {
    var data = {"username": user, "team": id}
    fetch(apiURL + 'api/manage/?method=favourite', {
        method:"post",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
    .then(() => {
        location.reload()
    })
    .catch(err => {
        console.log(err)
    })
}

function LeaveTeam(e, user, redirect) {
    var data = JSON.stringify({"username": user, "team": e.id})
    fetch(apiURL + 'api/manage/?method=leave', {
        method: "post",
        body: data,
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(() => {
        if (redirect) {
            location.replace(location.origin + "/teams")
        } else {
            location.reload()
        }
    })
    .catch(err => {
        console.log(err)
    })
}