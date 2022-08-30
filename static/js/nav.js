
var sideNav = document.getElementById("sideNav");

function w3_open() {
    if (mySidenav.style.display === 'block') {
        mySidenav.style.display = 'none';
        overlayBg.style.display = "none";
    } else {
        mySidenav.style.display = 'block';
        overlayBg.style.display = "block";
    }
}

function w3_close() {
    mySidenav.style.display = "none";
    overlayBg.style.display = "none";
}


