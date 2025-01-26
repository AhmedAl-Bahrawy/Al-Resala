// إضافة بعض الرسوم المتحركة عند تحميل الصفحة
window.addEventListener('DOMContentLoaded', () => {
    const heroText = document.querySelector('.hero h1');
    heroText.style.opacity = '0';
    heroText.style.transform = 'translateY(20px)';
    setTimeout(() => {
      heroText.style.transition = 'all 0.6s ease';
      heroText.style.opacity = '1';
      heroText.style.transform = 'translateY(0)';
    }, 300);
    
  });
  
  particlesJS("particles-js", {
    particles: {
      number: { value: 100 },
      size: { value: 3 },
      move: { enable: true, speed: 2 },
      line_linked: { enable: true, distance: 150 },
      color: { value: "#ffffff" },
    },
    interactivity: {
      events: {
        onhover: { enable: true, mode: "repulse" },
        onclick: { enable: true, mode: "push" },
      },
    },
  });
  
