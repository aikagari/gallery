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

//video
window.onkeydown = function( event ) {
    if ( event.keyCode == 27 ) {
        list_item = document.querySelectorAll('[id^=light]');
        for (var i=0; i < list_item.length; i++) {
            if (list_item[i].style.display == 'block') {
                lightbox_close(list_item[i].dataset.name);
                break;
            }
        }
    }
};


function lightbox_open(video_id) {
  var lightBoxVideo = document.getElementById(video_id);
  window.scrollTo(0, 0);
  video = document.getElementById('light'+video_id);
  document.getElementById('light'+video_id).style.display = 'block';
  document.getElementById('fade'+video_id).style.display = 'block';
  lightBoxVideo.play();
}

function lightbox_close(video_id) {
  var lightBoxVideo = document.getElementById(video_id);
  document.getElementById('light'+video_id).style.display = 'none';
  document.getElementById('fade'+video_id).style.display = 'none';
  lightBoxVideo.pause();
  lightBoxVideo.currentTime = 0;
}
