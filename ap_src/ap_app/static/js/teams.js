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

/*
Leaves team but also checks for lingering permissions and removes them
*/
async function LeaveTeamAndRemovePermissions(e, user, token) {
    const headers = {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    };
  
    var data = JSON.stringify({ username: user, team: e.id });
  
    const leaveResponse = await fetch(apiURL + "api/manage/?method=leave", {
      method: "post",
      body: data,
      headers: headers,
    });
  
    if (!leaveResponse.ok)
      throw new Error(`Leave request failed with status ${leaveResponse.status}`);
  
    const leaveData = await leaveResponse.json();
  
    if (leaveData.message === "success") {
      const permissionsResponse = await fetch(
        window.location.origin + "/remove_lingering_perms",
        {
          method: "post",
          body: data,
          headers: headers,
        },
      );
  
      if (!permissionsResponse.ok)
        throw new Error(
          `Permissions check request failed with status ${permissionsResponse.status}`,
        );
  
      const permissionsData = await permissionsResponse.json();
      location.replace(location.origin + "/teams")
    }
  }

function DeleteTeam(e) {
    var data = JSON.stringify({"id": e.id})
    fetch(apiURL + 'api/teams/?method=delete&format=json', {
        method: "post",
        body: data,
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(() => {
        location.replace(location.origin + "/teams")
    })
    .catch(err => {
        console.log(err)
    })
}