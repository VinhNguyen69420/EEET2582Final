// Function to toggle responsive class for the navigation menu
function myMenuFunction() {
    var i = document.getElementById("navMenu");

    // Check if the current class is "nav-menu" and toggle to "responsive" if true, or revert to "nav-menu" otherwise
    if (i.className === "nav-menu") {
        i.className += " responsive";
    } else {
        i.className = "nav-menu";
    }
}

// DOM elements for login and register buttons, as well as login and register containers
var a = document.getElementById("loginBtn");
var b = document.getElementById("registerBtn");
var x = document.getElementById("login");
var y = document.getElementById("register");

// Function to display the login container and adjust styles accordingly
function login() {
    x.style.left = "4px";
    y.style.right = "-520px";
    a.className += " white-btn";  // Add white-btn class to login button
    b.className = "btn";  // Reset register button class to default btn
    x.style.opacity = 1;  // Set login container opacity to fully visible
    y.style.opacity = 0;  // Set register container opacity to fully transparent
}

// Function to display the register container and adjust styles accordingly
function register() {
    x.style.left = "-510px";
    y.style.right = "5px";
    a.className = "btn";  // Reset login button class to default btn
    b.className += " white-btn";  // Add white-btn class to register button
    x.style.opacity = 0;  // Set login container opacity to fully transparent
    y.style.opacity = 1;  // Set register container opacity to fully visible
}