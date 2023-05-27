function validateForm() {
    var username = document.getElementById("username").value;
    if (username.trim() == "") {
      document.getElementById("usernameError").style.display = "block";
      return false;
    }
    return true;
  }
  