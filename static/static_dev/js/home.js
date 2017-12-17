// Центрирование картинки и цены в карточке товара на главной странице

var imgs = document.querySelectorAll('.center-core img');
var div_of_imgs_width = document.getElementsByClassName('center-core')[0].clientWidth

for (let img of imgs){
    var new_img_left = Math.floor((div_of_imgs_width - img.clientWidth) / 2);
    img.style.left = new_img_left + 'px';
}