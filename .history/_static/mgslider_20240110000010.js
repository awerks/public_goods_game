mgslider.prototype.hide = function () {
    document.getElementById(this.id()).style.display = "block";
    document.getElementById(this.id("show")).style.visibility = "visible";
    document.getElementById(this.id("show")).style.textAlign = "left";
    document.getElementById(this.id("before")).style.display = "none";
};
