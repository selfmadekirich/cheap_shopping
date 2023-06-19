//mobile
const burger = document.getElementById('burger')
const menu = document.getElementById('menu')

burger.addEventListener('click', () => 
{menu.classList.toggle('is-active'); });

function EnableButton(){
    if(this.value){
      document.getElementById("bttn").disabled = false;
    }
    else 
    document.getElementById("bttn").disabled = true;
   }

function AnyCheckboxSelected(){
       const btn = document.querySelector('#btn');
            let checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            if(checkboxes.length > 0 )
              btn.disabled = false;
            else 
             btn.disabled = true;       
}   