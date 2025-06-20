function togglePassword(element) {
    const passwordInput = document.getElementsByName("password")[0];
    const icon = element.querySelector(".toggle-icon")

    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      icon.classList.remove("fa-eye");
      icon.classList.add("fa-eye-slash");
    } else {
      passwordInput.type = "password";
      icon.classList.remove("fa-eye-slash");
      icon.classList.add("fa-eye");
  }
}

function togglePasswords() {
  const pass1 = document.getElementById("id_password1");
  const pass2 = document.getElementById("id_password2");
  const show = document.getElementById("showPassword").checked;

  if (pass1) pass1.type = show ? "text" : "password";
  if (pass2) pass2.type = show ? "text" : "password";
}