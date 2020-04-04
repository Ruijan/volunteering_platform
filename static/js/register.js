function showDiv(divToHide, divToShow){
    document.getElementById(divToHide).style.display = "none";
    document.getElementById(divToShow).style.display = "block";
}

function selectSkill(skillName, skills){
    if(skills.includes(skillName)){
        for( var i = 0; i < skills.length; i++){ if ( skills[i] === skillName) { skills.splice(i, 1); }}
        document.getElementById(skillName + "_skill").style.backgroundColor = "grey"
    }
    else{
        skills.push(skillName);
        document.getElementById(skillName + "_skill").style.backgroundColor = "lightblue"
    }
}

var password = document.getElementById("pass");
var confirm_password = document.getElementById("pass2");

function validatePassword(){
  if(password.value != confirm_password.value) {
    confirm_password.setCustomValidity("Passwords Don't Match");
  } else {
    confirm_password.setCustomValidity('');
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;

