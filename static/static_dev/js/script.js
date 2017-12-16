

// Появление списка корзины при наведении на кнопку "Корзина"

var bask = document.getElementsByClassName("basket");

var bask_btn = document.getElementById("basket-btn");

bask_btn.onmouseover = function (e) {
    $(".basket").removeClass('hidden');
};

bask_btn.onmouseout = function (e) {
    $(".basket").addClass('hidden')
};




// Центрирование картинки и цены в карточке товара на главной странице

var imgs = document.querySelectorAll('.center-core img');
var div_of_imgs_width = document.getElementsByClassName('center-core')[0].clientWidth

for (let img of imgs){
    var new_img_left = Math.floor((div_of_imgs_width - img.clientWidth) / 2);
    img.style.left = new_img_left + 'px';
}


