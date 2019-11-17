// button video/image, need to replace to tabs
function openPage(pageName, elmnt, color) {
  let i, tabContent, tabLinks;
  tabContent = document.getElementsByClassName("tabContent");
  for (i = 0; i < tabContent.length; i++) {
    tabContent[i].style.display = "none";
  }

  tabLinks = document.getElementsByClassName("tabLinks");
  for (i = 0; i < tabLinks.length; i++) {
    tabLinks[i].style.backgroundColor = "";
  }

  document.getElementById(pageName).style.display = "block";
  elmnt.style.backgroundColor = color;
}

// lazy load images
document.addEventListener("DOMContentLoaded", function() {
  const imageObserver = new IntersectionObserver((entries, imgObserver) => {
      entries.forEach((entry) => {
          if (entry.isIntersecting) {
              const lazyImage = entry.target;
              console.log("lazy loading ", lazyImage);
              lazyImage.src = lazyImage.dataset.src;
              lazyImage.classList.remove("lzy_img");
              imgObserver.unobserve(lazyImage);
          }
      })
  });
  const arr = document.querySelectorAll('img.lzy_img');
  arr.forEach((v) => {
      imageObserver.observe(v);
  })
});
