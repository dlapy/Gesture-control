content = document.querySelector(".content")

function left(){
    content.classList.remove("right");
    content.classList.remove("center");
    content.classList.add("left");
}
function right(){
    content.classList.add("right");
    content.classList.remove("left");
    content.classList.remove("center");
}
function center(){
    content.classList.add("center");
    content.classList.remove("left");
    content.classList.remove("right");
}

act = false

function activ_auto_btn(){
        eel.auto_lock();
        if (act == false){
            act = true
            document.querySelector(".act").classList.add("active");
        }else{
            act = false
            document.querySelector(".act").classList.remove("active");
        }
}

act2 = false

function activ_present_btn(){
    eel.present_lock();
    if (act2 == false){
        act2 = true
        document.querySelector(".act2").classList.add("active");
    }else{
        act2 = false
        document.querySelector(".act2").classList.remove("active");
    }

}