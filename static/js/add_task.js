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

function selectEmergency(emergency){
    emergencies = document.getElementsByClassName("emergency_button");
    for (level in emergencies){
        if (emergencies[level].innerHTML){
            emergencies[level].style.backgroundColor = "whitesmoke";
            emergencies[level].style.boxShadow = "0px";
        }
    }
    document.getElementById(emergency).style.backgroundColor= "lightblue"
    document.getElementById("selected_emergency").value = emergency;
}

function showDiv(divToHide, divToShow){
    document.getElementById(divToHide).style.display = "none";
    document.getElementById(divToShow).style.display = "block";
}
