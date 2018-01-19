// Centralization of img in product_item div

var imgs = document.querySelectorAll('.center-core img');
var div_of_imgs_width = document.getElementsByClassName('center-core')[0].clientWidth;

imgs.forEach(function(img){
    var new_img_left = Math.floor((div_of_imgs_width - img.clientWidth) / 2);
    img.style.left = new_img_left + 'px';
});





