

// Появление списка корзины при наведении на кнопку "Корзина"


var bask_btn = document.getElementById("basket-btn");

bask_btn.onmouseover = function (e) {
    $(".basket").removeClass('hidden');
};

bask_btn.onmouseout = function (e) {
    $(".basket").addClass('hidden')
};






