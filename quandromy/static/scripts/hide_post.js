
//Make the request when the window loads
window.onload = function (){
	hide = document.querySelector(".hide-element");
	hide.onclick = function (){
	this.parentElement.parentElement.parentElement.parentElement.remove();
	};
};
