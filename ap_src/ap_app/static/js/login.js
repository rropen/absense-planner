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

function togglePasswords(checkboxElement) {
  const passwords = document.querySelectorAll(".password-input");
  for (const passwordInput of passwords) {
    if (passwordInput) passwordInput.type = checkboxElement.checked ? "text" : "password";
  }
}