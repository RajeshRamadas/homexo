
/*Animated cursor  */

/*global document: false */
var cursor = document.getElementById("cursor");
var cursor2 = document.getElementById("cursor2");
var cursor3 = document.getElementById("cursor3");
var x, y;

document.getElementsByTagName("body")[0].addEventListener("mousemove", function (moveover) {
    "use strict";
    cursor.style.left = moveover.clientX + "px";
    cursor.style.top = moveover.clientY + "px";
    cursor2.style.left = moveover.clientX + "px";
    cursor2.style.top = moveover.clientY + "px";
    cursor3.style.left = moveover.clientX + "px";
    cursor3.style.top = moveover.clientY + "px";
});


function moveover() {
    "use strict";
    cursor2.classList.add("hover", "hover-2");
    cursor3.classList.add("hover", "hover-2");
}
function mouseout() {
    "use strict";
    cursor2.classList.remove("hover", "hover-2");
    cursor3.classList.remove("hover", "hover-2");
}
mouseout();

function eventtrigger(cursor) {
    "use strict";
    cursor.addEventListener("mouseover", moveover);
    cursor.addEventListener("mouseout", mouseout);
}


for (x = document.querySelectorAll(".hover-target, .hover-target-2"), y = x.length - 1; y >= 0; y = y - 1) {
    eventtrigger(x[y]);
}

/**** Slider and dot navigation */


const track = document.querySelector('.carousel_track');
const slides = Array.from(track.children)

const nextButton = document.querySelector('.carousel_button--right');
const prevtButton = document.querySelector('.carousel_button--left');

const dotsNav = document.querySelector('.carousel_nav');

const dots = Array.from(dotsNav.children)

const slideWidth = slides[0].getBoundingClientRect().width;

const setSlidePostion = (slide, index) => {
    slide.style.left = slideWidth * index + 'px'
};

slides.forEach(setSlidePostion);

const moveToSlide = (track, currentSlide, targetSlide) => {
    track.style.transform = 'translateX(-' + targetSlide.style.left; + ')';
    currentSlide.classList.remove('current-slide');
    targetSlide.classList.add('current-slide');

    currentSlide.querySelector('.c-hero__headline').classList.remove('reveal-text');
    currentSlide.querySelector('.c-hero__subheadline').classList.remove('reveal-text');
    currentSlide.querySelector('.c-hero__Para').classList.remove('reveal-text');

    targetSlide.querySelector('.c-hero__headline').classList.add('reveal-text');
    targetSlide.querySelector('.c-hero__subheadline').classList.add('reveal-text');
    targetSlide.querySelector('.c-hero__Para').classList.add('reveal-text');
}


const HideShowArrows = (slides, prevtButton, nextButton, targetIndex) => {

    if (targetIndex === 0) {
        prevtButton.classList.add('is-hidden');
        nextButton.classList.remove('is-hidden');
    } else if (targetIndex === slides.length - 1) {
        prevtButton.classList.remove('is-hidden');
        nextButton.classList.add('is-hidden');
    }
    else {
        prevtButton.classList.remove('is-hidden');
        nextButton.classList.remove('is-hidden');
    }
}

nextButton.addEventListener('click', e => {


    const currentSlide = track.querySelector('.current-slide');
    const nextSlide = currentSlide.nextElementSibling;
    const currentDot = dotsNav.querySelector('.current-slide');
    const nextDot = currentDot.nextElementSibling;
    const nextIndex = slides.findIndex(slide => slide === nextSlide);
    moveToSlide(track, currentSlide, nextSlide);
    updateDots(currentDot, nextDot);
    HideShowArrows(slides, prevtButton, nextButton, nextIndex);

});


prevtButton.addEventListener('click', e => {


    const currentSlide = track.querySelector('.current-slide');
    const prevSlide = currentSlide.previousElementSibling;
    const currentDot = dotsNav.querySelector('.current-slide');
    const prevDot = currentDot.previousElementSibling;
    const prevIndex = slides.findIndex(slide => slide === prevSlide);
    moveToSlide(track, currentSlide, prevSlide);
    updateDots(currentDot, prevDot);
    HideShowArrows(slides, prevtButton, nextButton, prevIndex);
});

const updateDots = (currentDot, targetDot) => {
    currentDot.classList.remove('current-slide');
    targetDot.classList.add('current-slide');
}

dotsNav.addEventListener('click', e => {

    const targetDot = e.target.closest('button');
    /*console.log(targetDot);*/
    if (!targetDot) return;
    const currentSlide = track.querySelector('.current-slide');
    const currentDot = dotsNav.querySelector('.current-slide');
    const targetIndex = dots.findIndex(dot => dot === targetDot);
    const targetSlide = slides[targetIndex];

    moveToSlide(track, currentSlide, targetSlide);
    updateDots(currentDot, targetDot);

    HideShowArrows(slides, prevtButton, nextButton, targetIndex);



})



if (window.addEventListener) {
    // Firefox
    document.addEventListener('DOMMouseScroll', function (e) {
        handleMouseWheelDirection(detectMouseWheelDirection(e));
    });

    // IE9, Chrome, Safari, Opera
    document.addEventListener('mousewheel', function (e) {
        handleMouseWheelDirection(detectMouseWheelDirection(e));
    });
}
else {
    // IE 6/7/8
    document.attachEvent("onmousewheel", function (e) {
        handleMouseWheelDirection(detectMouseWheelDirection(e));
    });
}



function detectMouseWheelDirection(e) {
    var delta = null,
        direction = false
        ;
    if (!e) { // if the event is not provided, we get it from the window object
        e = window.event;
    }
    if (e.wheelDelta) { // will work in most cases
        delta = e.wheelDelta / 60;
    } else if (e.detail) { // fallback for Firefox
        delta = -e.detail / 2;
    }
    if (delta !== null) {
        direction = delta > 0 ? 'up' : 'down';
    }

    return direction;
}


// Updated event listener setup
document.addEventListener('DOMContentLoaded', function() {
    const sideMenuButtons = document.getElementsByClassName("nav-active");
    const hamMenuButtons = document.getElementsByClassName("menu-nav");
    
    // Add click handlers for side menu
    for (let i = 0; i < sideMenuButtons.length; i++) {
        sideMenuButtons[i].addEventListener("click", function(e) {
            e.preventDefault();
            handleSidemenu('', i);
        });
    }
    
    // Add click handlers for hamburger menu
    for (let i = 0; i < hamMenuButtons.length; i++) {
        hamMenuButtons[i].addEventListener("click", function(e) {
            e.preventDefault();
            handleSidemenu('', i);
            
            // Close hamburger menu after selection
            const checkbox = document.getElementById('toggle-checkbox');
            if (checkbox) {
                checkbox.checked = false;
            }
        });
    }
});

// Fixed scroll wheel navigation with proper side menu updates
function handleMouseWheelDirection(direction) {
    const currentSlide = track.querySelector('.current-slide');
    const currentSlideIndex = slides.findIndex(slide => slide === currentSlide);
    
    if (direction == 'down') {
        const nextSlide = currentSlide.nextElementSibling;
        if (!nextSlide) return; // Don't go past last slide
        
        const currentDot = dotsNav.querySelector('.current-slide');
        const nextDot = currentDot.nextElementSibling;
        const nextIndex = slides.findIndex(slide => slide === nextSlide);
        
        moveToSlide(track, currentSlide, nextSlide);
        updateDots(currentDot, nextDot);
        updateSideMenuSelection(nextIndex);
        HideShowArrows(slides, prevtButton, nextButton, nextIndex);
        
    } else if (direction == 'up') {
        const prevSlide = currentSlide.previousElementSibling;
        if (!prevSlide) return; // Don't go past first slide
        
        const currentDot = dotsNav.querySelector('.current-slide');
        const prevDot = currentDot.previousElementSibling;
        const prevIndex = slides.findIndex(slide => slide === prevSlide);
        
        moveToSlide(track, currentSlide, prevSlide);
        updateDots(currentDot, prevDot);
        updateSideMenuSelection(prevIndex);
        HideShowArrows(slides, prevtButton, nextButton, prevIndex);
    }
}


/********************************** */



/**** Side menu and hamburger link */

var side_menu_button = document.getElementsByClassName("nav-active");
var ham_menu_button = document.getElementsByClassName("menu-nav");

function handleSidemenu(sel_class, sel_index) {
    'use strict';
    
    // Prevent default link behavior
    event.preventDefault();
    
    const currentSlide = track.querySelector('.current-slide');
    const targetSlide = slides[sel_index];
    
    // Only proceed if target slide exists
    if (!targetSlide) return;
    
    moveToSlide(track, currentSlide, targetSlide);
    HideShowArrows(slides, prevtButton, nextButton, sel_index);

    // Update dot indicators
    const dotIndicators = document.getElementsByClassName("carousel__indicator");
    for (let x = 0; x < dotIndicators.length; x++) {
        dotIndicators[x].classList.remove('current-slide');
    }
    
    if (dotIndicators[sel_index]) {
        dotIndicators[sel_index].classList.add('current-slide');
    }

    // Update side menu active states
    updateSideMenuSelection(sel_index);
}

// Function to update side menu selection
function updateSideMenuSelection(targetIndex) {
    const sideMenuItems = document.getElementsByClassName("nav-active");
    
    // Remove all selected classes
    const selectedClasses = [
        'selected-nav-ma', 'selected-nav-design', 'selected-nav-dev', 
        'selected-nav-app', 'selected-nav-digimarket', 'selected-nav-price', 
        'selected-nav-about'
    ];
    
    for (let i = 0; i < sideMenuItems.length; i++) {
        selectedClasses.forEach(className => {
            sideMenuItems[i].classList.remove(className);
        });
    }
    
    // Add the correct selected class based on index
    const classesToAdd = [
        'selected-nav-ma',       // Index 0 - HOMEXO
        'selected-nav-design',   // Index 1 - Property  
        'selected-nav-dev',      // Index 2 - Legal Consulting
        'selected-nav-app',      // Index 3 - Finance
        'selected-nav-digimarket', // Index 4 - Asset Care
        'selected-nav-about'     // Index 5 - About us
    ];
    
    if (sideMenuItems[targetIndex] && classesToAdd[targetIndex]) {
        sideMenuItems[targetIndex].classList.add(classesToAdd[targetIndex]);
    }
}


var selecSideMenu_scroll = function () {


    'use strict';
    var currentSlide = track.querySelector('.current-slide');
    var targetSlide = slides[sel_index];
    moveToSlide(track, currentSlide, targetSlide);
    HideShowArrows(slides, prevtButton, nextButton, sel_index);

    var ham_menu_button = document.getElementsByClassName("carousel__indicator");


    for (x = 0; x < ham_menu_button.length; x++) {
        ham_menu_button[x].classList.remove('current-slide');
    }

    ham_menu_button[sel_index].classList.add('current-slide');

}






var updateSideMenuDown = function () {
	
	 for (x = 0; x < side_menu_button.length; x++) {
		 if(side_menu_button[x].classList.length===3)
		 {
		 switch (side_menu_button[x].classList[2]) {
            case "selected-nav-ma":
                side_menu_button[0].classList.remove('selected-nav-ma'); 
				side_menu_button[1].classList.add('selected-nav-design');
				return;
            case "selected-nav-design":
                side_menu_button[1].classList.remove('selected-nav-design');
				side_menu_button[2].classList.add('selected-nav-dev');
                return;
            case "selected-nav-dev":
               side_menu_button[2].classList.remove('selected-nav-dev');
				side_menu_button[3].classList.add('selected-nav-app');
                return;
            case "selected-nav-app":
                side_menu_button[3].classList.remove('selected-nav-app');
				side_menu_button[4].classList.add('selected-nav-digimarket');
                return;
            case "selected-nav-digimarket":
                side_menu_button[4].classList.remove('selected-nav-digimarket');
				side_menu_button[5].classList.add('selected-nav-price');
                return;
            case "selected-nav-price":
                side_menu_button[5].classList.remove('selected-nav-price');
				side_menu_button[6].classList.add('selected-nav-about');
                return;
            case "selected-nav-about":
                return;

			}
		 }

    }	
}

var updateSideMenuUp = function () {
	
    for (x = 0; x < side_menu_button.length; x++) {
        if(side_menu_button[x].classList.length===3)
        {
        switch (side_menu_button[x].classList[2]) {
           case "selected-nav-ma":
               return;
               
           case "selected-nav-design":
                side_menu_button[0].classList.add('selected-nav-ma'); 
                side_menu_button[1].classList.remove('selected-nav-design');
               return;
           case "selected-nav-dev":
                side_menu_button[1].classList.add('selected-nav-design');
                side_menu_button[2].classList.remove('selected-nav-dev');
               return;
           case "selected-nav-app":
                side_menu_button[2].classList.add('selected-nav-dev');
                side_menu_button[3].classList.remove('selected-nav-app');
               return;
           case "selected-nav-digimarket":
                side_menu_button[3].classList.add('selected-nav-app');
                side_menu_button[4].classList.remove('selected-nav-digimarket');
               return;
           case "selected-nav-price":
                side_menu_button[4].classList.add('selected-nav-digimarket');
                side_menu_button[5].classList.remove('selected-nav-price');
               return;
           case "selected-nav-about":
                side_menu_button[5].classList.add('selected-nav-price');
                side_menu_button[6].classList.remove('selected-nav-about');
               return;

           }
        }

   }	
}

var selecSideMenu = function () {

    "use strict";
    var sel_index = 0, checkbox;

    if (this.classList[0] !== "nav-active") {
        checkbox = document.getElementById('toggle-checkbox');
        checkbox.checked =  checkbox.checked ^ 1;
    }



    side_menu_button[5].classList.remove('selected-nav-price');
    side_menu_button[6].classList.remove('selected-nav-about');
    side_menu_button[4].classList.remove('selected-nav-digimarket');
    side_menu_button[3].classList.remove('selected-nav-app');
    side_menu_button[2].classList.remove('selected-nav-dev');
    side_menu_button[1].classList.remove('selected-nav-design');
    side_menu_button[0].classList.remove('selected-nav-ma');


    for (x = 0; x < this.classList.length; x = x +1) {
        /*console.log(this.classList[x]);*/

        switch (this.classList[x]) {
        case "nav-active-ma":
            side_menu_button[0].classList.add('selected-nav-ma');
            handleSidemenu(this.classList[x], sel_index);
            break;
        case "nav-active-design":
            side_menu_button[1].classList.add('selected-nav-design');
            handleSidemenu(this.classList[x], sel_index + 1);
            break;
        case "nav-active-dev":
            side_menu_button[2].classList.add('selected-nav-dev');
            handleSidemenu(this.classList[x], sel_index + 2);
            break;
        case "nav-active-app":
            side_menu_button[3].classList.add('selected-nav-app');
            handleSidemenu(this.classList[x], sel_index + 3);
            break;
        case "nav-active-digimarket":
            side_menu_button[4].classList.add('selected-nav-digimarket');
            handleSidemenu(this.classList[x], sel_index + 4);
            break;
        case "nav-active-price":
            side_menu_button[5].classList.add('selected-nav-price');
            handleSidemenu(this.classList[x], sel_index + 5);
            break;
        case "nav-active-about":
            side_menu_button[6].classList.add('selected-nav-about');
            handleSidemenu(this.classList[x], sel_index + 6);
            break;

        }

    }

}

for (var i = 0; i < side_menu_button.length; i++) {
    side_menu_button[i].addEventListener("click", selecSideMenu);
}

for (var i = 0; i < ham_menu_button.length; i++) {
    ham_menu_button[i].addEventListener("click", selecSideMenu);
}


/**** Side menu and hamburger link end */

/********************************** */


/* Data VidUp */

/* Get all elements with data-vidup */
const vidupElements = document.querySelectorAll('[data-vidup]');

const modal = document.getElementById('modal');
const modalVideo = document.getElementById('modal-video');
const mdc = document.getElementById('mdc');
const close = document.getElementById('close');

function closeModal() {
    // mdc.style.width = "0";
    mdc.style.transform = "scale(0)";

    setTimeout(() => {
        modal.style.visibility = "hidden";
        modal.style.opacity = "0";
        modalVideo.src = "";
    }, 500);
}

function showModal(element) {
    modal.style.visibility = "visible";
    modal.style.opacity = "1";
    modalVideo.src = element.href;
    mdc.style.width = "100%";


    setTimeout(() => {
        mdc.style.transform = "scale(1)";
    }, 300);

}

/* Foreach element add an eventlistener and show the popup when clicked and add the src in the link */
vidupElements.forEach(element => {
    element.addEventListener("click", (e) => {

        e.preventDefault();
        showModal(element);
    });
});

close.addEventListener('click', (e) => {
    closeModal();
});

mdc.addEventListener('click', () => {
    closeModal();
});

modal.addEventListener('click', () => {
    closeModal();
});


/********************************** */


/*code to move background logo*/
var bg_logo = document.querySelector("#bg_logo");

bg_logo.addEventListener("mousemove", (event) => {
    if (screen.width > 900) {
        bg_logo.style.backgroundPositionX = (-event.offsetX * 1) / 100 + "px";
        bg_logo.style.backgroundPositionY = (-event.offsetY * 1) / 100 + "px";
    }
});



function manageBannerVisibility() {
    const banner = document.querySelector('.cta_banner');
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    // Hide only on small laptops (tablet landscape to small laptop range)
    if (width >= 768 && width <= 1366 && height >= 600) {
        banner.style.display = 'none';
    } else {
        // Show on mobile phones (< 768px) and larger laptops (> 1366px)
        banner.style.display = 'flex';
    }
}

// Run on page load and window resize
window.addEventListener('load', manageBannerVisibility);
window.addEventListener('resize', manageBannerVisibility);






