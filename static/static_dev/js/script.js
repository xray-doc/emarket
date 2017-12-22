$(document).ready(function () {

    // Появление списка корзины при наведении на кнопку "Корзина"

    $("#basket-btn").mouseover(function (e) {
        $(".basket").removeClass('hidden');
    });
    $('#basket-btn').mouseout(function (e) {
        $(".basket").addClass('hidden')
    });


    // Добавление товара в список при нажатии кнопки "Добавить в корзину"

    $('#form_buying_product').on('submit', function (e) {
        e.preventDefault()
        var nmb = $('#num-products-input').val()

        var submit_btn = $('#submit-btn');
        var product_name = submit_btn.data('name');
        var product_price = submit_btn.data('price');

        $('.container .basket ul').append('<li>'+product_name+', '+nmb+' шт., по '+product_price+'</li>')
    })


});






