function selectSkill(skillName){
    skills = document.getElementsByClassName("skill_button");
    for (skill in skills){
        if (skills[skill].innerHTML){
            skills[skill].style.backgroundColor = "whitesmoke";
        }
    }
    document.getElementById(skillName).style.backgroundColor= "lightblue"
    document.getElementById("selected_skill").value = skillName;
}

function showDiv(divToHide, divToShow){
    document.getElementById(divToHide).style.display = "none";
    document.getElementById(divToShow).style.display = "block";
}
