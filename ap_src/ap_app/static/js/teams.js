function JoinTeam(e) {
    console.log(e.dataset.username)
    console.log(e.dataset.team)
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
    var data = JSON.stringify({"username":user,"team":id})
    fetch('http://localhost:8000/api/manage/?method=favourite', {
        method:"POST",
        body:data,
    })
    .then(()=>{
        location.reload()
    })
}