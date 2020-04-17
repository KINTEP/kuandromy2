	//Define all functions and variables that will be needed
// Start with first post.
let counter = 1;

// Load posts 20 at a time.
const quantity = 10;

//When DOM Loads, render the first 20 posts
//window.onload = load();
//document.documentElement.scrollTop = 0;

window.onload = function () {
    document.documentElement.scrollTop = 0;
    load();
};


//document.addEventListener('DOMContentLoaded', load);

//What happens when the window is scrolled
 window.onscroll = () => {

    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
         load();

         }
     };

//The function that makes the request and loads the page
function load(){

	const start = counter;
    const end = start + quantity - 1;
    counter = end + 1;

	let request = new XMLHttpRequest();
    request.open("POST", "/ajax", true);
	request.onload = function(){
		response = request.responseText;
		data1 = JSON.parse(response);
        data1 = data1.data;
		 data1.forEach(add_post);
	}; 
    const data = new FormData();
    data.append('start', start);
    data.append('end', end);
	request.send(data);
    //xhttp.send("start=${start}&end={Ford}");
return false;
};

function add_post(contents) {
	// Create new post.
   	const post = document.createElement('div');
    post.className = 'post';
     post.innerHTML = contents;

     // Add post to DOM.
    document.querySelector('#posts').append(post);
     };