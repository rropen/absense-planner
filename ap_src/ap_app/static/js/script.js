// script.js

// Get the modal
var modal = document.getElementById("alertModal");

// Get the button that opens the modal
var btn = document.getElementById("question-mark");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// Get the OK button
var okButton = document.getElementById("alert-ok-button");

// When the user clicks the button, open the modal
btn.onclick = function () {
  modal.style.display = "block";
};

// When the user clicks on <span> (x), close the modal
span.onclick = function () {
  modal.style.display = "none";
};

// When the user clicks the OK button, close the modal
okButton.onclick = function () {
  modal.style.display = "none";
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};
