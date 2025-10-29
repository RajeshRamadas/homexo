/**
 * Modern JavaScript Refactored - script.js
 * Improved performance, readability, and maintainability
 */

// ========================================
// CONSTANTS & CONFIGURATION
// ========================================
const CONFIG = {
  wheelScrollDelay: 100, // Debounce delay for scroll
  animationDuration: 500,
  desktopMinWidth: 900
};

// ========================================
// CUSTOM CURSOR
// ========================================
const CustomCursor = (() => {
  const cursor = document.getElementById("cursor");
  const cursor2 = document.getElementById("cursor2");
  const cursor3 = document.getElementById("cursor3");

  const updatePosition = (e) => {
    const { clientX, clientY } = e;
    const posX = `${clientX}px`;
    const posY = `${clientY}px`;
    
    cursor.style.left = posX;
    cursor.style.top = posY;
    cursor2.style.left = posX;
    cursor2.style.top = posY;
    cursor3.style.left = posX;
    cursor3.style.top = posY;
  };

  const addHoverEffect = () => {
    cursor2.classList.add("hover", "hover-2");
    cursor3.classList.add("hover", "hover-2");
  };

  const removeHoverEffect = () => {
    cursor2.classList.remove("hover", "hover-2");
    cursor3.classList.remove("hover", "hover-2");
  };

  const init = () => {
    document.body.addEventListener("mousemove", updatePosition);
    
    const hoverTargets = document.querySelectorAll(".hover-target, .hover-target-2");
    hoverTargets.forEach(target => {
      target.addEventListener("mouseover", addHoverEffect);
      target.addEventListener("mouseout", removeHoverEffect);
    });
    
    removeHoverEffect(); // Initial state
  };

  return { init };
})();

// ========================================
// CAROUSEL CONTROLLER
// ========================================
const CarouselController = (() => {
  const track = document.querySelector('.carousel_track');
  const slides = Array.from(track?.children || []);
  const nextButton = document.querySelector('.carousel_button--right');
  const prevButton = document.querySelector('.carousel_button--left');
  const dotsNav = document.querySelector('.carousel_nav');
  const dots = Array.from(dotsNav?.children || []);

  let isAnimating = false;

  // Calculate slide position
  const setSlidePosition = (slide, index) => {
    const slideWidth = slide.getBoundingClientRect().width;
    slide.style.left = `${slideWidth * index}px`;
  };

  // Move to specific slide
  const moveToSlide = (currentSlide, targetSlide) => {
    if (isAnimating || !targetSlide) return;
    
    isAnimating = true;
    track.style.transform = `translateX(-${targetSlide.style.left})`;
    
    // Update slide classes
    currentSlide.classList.remove('current-slide');
    targetSlide.classList.add('current-slide');

    // Update text animations
    updateTextAnimations(currentSlide, targetSlide);
    
    setTimeout(() => { isAnimating = false; }, CONFIG.animationDuration);
  };

  // Update text reveal animations
  const updateTextAnimations = (currentSlide, targetSlide) => {
    const selectors = ['.c-hero__headline', '.c-hero__subheadline', '.c-hero__Para'];
    
    selectors.forEach(selector => {
      currentSlide.querySelector(selector)?.classList.remove('reveal-text');
      targetSlide.querySelector(selector)?.classList.add('reveal-text');
    });
  };

  // Update navigation dots
  const updateDots = (currentDot, targetDot) => {
    if (!currentDot || !targetDot) return;
    currentDot.classList.remove('current-slide');
    targetDot.classList.add('current-slide');
  };

  // Show/hide navigation arrows
  const updateArrows = (targetIndex) => {
    if (!prevButton || !nextButton) return;
    
    prevButton.classList.toggle('is-hidden', targetIndex === 0);
    nextButton.classList.toggle('is-hidden', targetIndex === slides.length - 1);
  };

  // Navigate to slide by index
  const navigateToSlide = (targetIndex) => {
    const currentSlide = track.querySelector('.current-slide');
    const targetSlide = slides[targetIndex];
    
    if (!targetSlide) return;
    
    moveToSlide(currentSlide, targetSlide);
    updateArrows(targetIndex);
    
    // Update dots if they exist
    if (dotsNav) {
      const currentDot = dotsNav.querySelector('.current-slide');
      const targetDot = dots[targetIndex];
      updateDots(currentDot, targetDot);
    }
    
    // Update side menu
    SideMenuController.updateSelection(targetIndex);
  };

  // Next slide handler
  const goToNextSlide = () => {
    const currentSlide = track.querySelector('.current-slide');
    const nextSlide = currentSlide.nextElementSibling;
    if (!nextSlide) return;
    
    const nextIndex = slides.findIndex(slide => slide === nextSlide);
    navigateToSlide(nextIndex);
  };

  // Previous slide handler
  const goToPrevSlide = () => {
    const currentSlide = track.querySelector('.current-slide');
    const prevSlide = currentSlide.previousElementSibling;
    if (!prevSlide) return;
    
    const prevIndex = slides.findIndex(slide => slide === prevSlide);
    navigateToSlide(prevIndex);
  };

  // Dot click handler
  const handleDotClick = (e) => {
    const targetDot = e.target.closest('button');
    if (!targetDot) return;
    
    const targetIndex = dots.findIndex(dot => dot === targetDot);
    navigateToSlide(targetIndex);
  };

  const init = () => {
    if (!track || slides.length === 0) return;
    
    // Set initial positions
    slides.forEach(setSlidePosition);
    
    // Add event listeners
    nextButton?.addEventListener('click', goToNextSlide);
    prevButton?.addEventListener('click', goToPrevSlide);
    dotsNav?.addEventListener('click', handleDotClick);
    
    // Initialize arrows
    updateArrows(0);
  };

  return { init, navigateToSlide };
})();

// ========================================
// MOUSE WHEEL NAVIGATION
// ========================================
const MouseWheelNavigation = (() => {
  let lastScrollTime = 0;
  
  const detectDirection = (e) => {
    let delta = null;
    
    if (e.wheelDelta) {
      delta = e.wheelDelta / 60;
    } else if (e.detail) {
      delta = -e.detail / 2;
    }
    
    return delta !== null ? (delta > 0 ? 'up' : 'down') : false;
  };

  const handleScroll = (e) => {
    const now = Date.now();
    if (now - lastScrollTime < CONFIG.wheelScrollDelay) return;
    
    lastScrollTime = now;
    
    const direction = detectDirection(e);
    if (!direction) return;
    
    const track = document.querySelector('.carousel_track');
    const currentSlide = track?.querySelector('.current-slide');
    if (!currentSlide) return;
    
    const slides = Array.from(track.children);
    const currentIndex = slides.findIndex(slide => slide === currentSlide);
    
    if (direction === 'down' && currentIndex < slides.length - 1) {
      CarouselController.navigateToSlide(currentIndex + 1);
    } else if (direction === 'up' && currentIndex > 0) {
      CarouselController.navigateToSlide(currentIndex - 1);
    }
  };

  const init = () => {
    // Modern wheel event
    document.addEventListener('wheel', handleScroll, { passive: true });
    
    // Legacy Firefox support
    document.addEventListener('DOMMouseScroll', handleScroll);
  };

  return { init };
})();

// ========================================
// SIDE MENU CONTROLLER
// ========================================
const SideMenuController = (() => {
  const CLASS_MAP = [
    'selected-nav-ma',       // Index 0 - HOMEXO
    'selected-nav-design',   // Index 1 - Property  
    'selected-nav-dev',      // Index 2 - Legal Consulting
    'selected-nav-app',      // Index 3 - Finance
    'selected-nav-digimarket', // Index 4 - Asset Care
    'selected-nav-about'     // Index 5 - About us
  ];

  const updateSelection = (targetIndex) => {
    const sideMenuItems = document.querySelectorAll(".nav-active");
    
    // Remove all selected classes
    sideMenuItems.forEach(item => {
      CLASS_MAP.forEach(className => item.classList.remove(className));
    });
    
    // Add correct selected class
    if (sideMenuItems[targetIndex] && CLASS_MAP[targetIndex]) {
      sideMenuItems[targetIndex].classList.add(CLASS_MAP[targetIndex]);
    }
  };

  const handleMenuClick = (e, index) => {
    e.preventDefault();
    CarouselController.navigateToSlide(index);
  };

  const init = () => {
    const sideMenuButtons = document.querySelectorAll(".nav-active");
    const hamMenuButtons = document.querySelectorAll(".menu-nav");
    
    // Side menu click handlers
    sideMenuButtons.forEach((button, index) => {
      button.addEventListener("click", (e) => handleMenuClick(e, index));
    });
    
    // Hamburger menu click handlers
    hamMenuButtons.forEach((button, index) => {
      button.addEventListener("click", (e) => {
        handleMenuClick(e, index);
        
        // Close hamburger menu
        const checkbox = document.getElementById('toggle-checkbox');
        if (checkbox) checkbox.checked = false;
      });
    });
  };

  return { init, updateSelection };
})();

// ========================================
// VIDEO MODAL CONTROLLER
// ========================================
const VideoModalController = (() => {
  const modal = document.getElementById('modal');
  const modalVideo = document.getElementById('modal-video');
  const mdc = document.getElementById('mdc');
  const closeBtn = document.getElementById('close');

  const closeModal = () => {
    mdc.style.transform = "scale(0)";
    
    setTimeout(() => {
      modal.style.visibility = "hidden";
      modal.style.opacity = "0";
      modalVideo.src = "";
    }, CONFIG.animationDuration);
  };

  const showModal = (videoUrl) => {
    modal.style.visibility = "visible";
    modal.style.opacity = "1";
    modalVideo.src = videoUrl;
    mdc.style.width = "100%";
    
    setTimeout(() => {
      mdc.style.transform = "scale(1)";
    }, 300);
  };

  const init = () => {
    if (!modal) return;
    
    // Video trigger elements
    const vidupElements = document.querySelectorAll('[data-vidup]');
    vidupElements.forEach(element => {
      element.addEventListener("click", (e) => {
        e.preventDefault();
        showModal(element.href);
      });
    });
    
    // Close handlers
    closeBtn?.addEventListener('click', closeModal);
    mdc?.addEventListener('click', closeModal);
    modal.addEventListener('click', closeModal);
  };

  return { init };
})();

// ========================================
// BACKGROUND PARALLAX EFFECT
// ========================================
const BackgroundParallax = (() => {
  const bgLogo = document.querySelector("#bg_logo");
  
  const handleMouseMove = (e) => {
    if (window.innerWidth <= CONFIG.desktopMinWidth) return;
    
    const { offsetX, offsetY } = e;
    bgLogo.style.backgroundPositionX = `${-offsetX / 100}px`;
    bgLogo.style.backgroundPositionY = `${-offsetY / 100}px`;
  };

  const init = () => {
    if (!bgLogo) return;
    bgLogo.addEventListener("mousemove", handleMouseMove);
  };

  return { init };
})();

// ========================================
// BANNER VISIBILITY MANAGER
// ========================================
const BannerVisibilityManager = (() => {
  const banner = document.querySelector('.cta_banner');
  
  const updateVisibility = () => {
    if (!banner) return;
    
    const { innerWidth: width, innerHeight: height } = window;
    
    // Hide on small laptops (768px - 1366px)
    if (width >= 768 && width <= 1366 && height >= 600) {
      banner.style.display = 'none';
    } else {
      banner.style.display = 'flex';
    }
  };

  const init = () => {
    if (!banner) return;
    
    updateVisibility();
    window.addEventListener('load', updateVisibility);
    window.addEventListener('resize', updateVisibility);
  };

  return { init };
})();

// ========================================
// APPLICATION INITIALIZATION
// ========================================
const App = (() => {
  const init = () => {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initializeModules);
    } else {
      initializeModules();
    }
  };

  const initializeModules = () => {
    try {
      CustomCursor.init();
      CarouselController.init();
      MouseWheelNavigation.init();
      SideMenuController.init();
      VideoModalController.init();
      BackgroundParallax.init();
      BannerVisibilityManager.init();
      
      console.log('✅ App initialized successfully');
    } catch (error) {
      console.error('❌ Error initializing app:', error);
    }
  };

  return { init };
})();

// Start the application
App.init();