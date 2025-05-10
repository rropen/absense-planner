/* var checkbox = document.getElementById('darkModeToggle');
var stylesheet = document.getElementById('darkSwitch');

document.addEventListener("DOMContentLoaded", function() {
    var darkState = localStorage.getItem("darkCheck");
    if (darkState == "true") {
        checkbox.checked = true;
        stylesheet.href = '/ap_src/ap_app/static/css/darkmode.css';
    } else {
        checkbox.checked = false;
        stylesheet.href = '/ap_src/ap_app/static/css/basic.css'
    }

    checkbox.addEventListener("change", function() {
        var darkCheck = checkbox.checked;
        localStorage.setItem("darkCheck", darkCheck);
        if (darkCheck) {
            stylesheet.href = '/ap_src/ap_app/static/css/darkmode.css'
        } else {
            stylesheet.href = '/ap_src/ap_app/static/css/basic.css'
        }
    });
}); */

function applyStylesheet() {
  let stylesheet = document.getElementById("darkSwitch");
  let darkState = localStorage.getItem("darkCheck");
  let darkModePath = localStorage.getItem("darkModePath");
  let lightModePath = localStorage.getItem("lightModePath");

  if (darkState === "true" && darkModePath) {
    stylesheet.href = darkModePath;
  } else if (lightModePath) {
    stylesheet.href = lightModePath;
  }
}

document.addEventListener("DOMContentLoaded", function () {
  applyStylesheet();
  let checkbox = document.getElementById("darkModeToggle");
  if (checkbox) {
    let paths = document.getElementById("stylesheet-paths");
    let darkModePath = paths.getAttribute("darkmode-location");
    let lightModePath = paths.getAttribute("lightmode-location");
    localStorage.setItem("darkModePath", darkModePath);
    localStorage.setItem("lightModePath", lightModePath);
    let darkState = localStorage.getItem("darkCheck");
    if (darkState === "true") {
      checkbox.checked = true;
    } else {
      checkbox.checked = false;
    }
    checkbox.addEventListener("change", function () {
      let darkCheck = checkbox.checked;
      localStorage.setItem("darkCheck", darkCheck.toString());
      applyStylesheet();
    });
  }
});
