function togglePassword() {
    const passwordInput = document.getElementById("id_password");
    const icon = document.getElementById("toggleIcon");

    if (!passwordInput) return;

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