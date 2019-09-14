
del = document.querySelector('.admin_del');
var clicked = false;
console.log("oui.")
del.addEventListener('click', function(e){
    if (!clicked)
    {
        e.preventDefault()
        del.style.left = "30px";
        clicked = true;
    }
}, false)