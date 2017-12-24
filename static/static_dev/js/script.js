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
        e.preventDefault();
        var form = $('#form_buying_product');
        var nmb = $('#num-products-input').val();

        var submit_btn = $('#submit-btn');
        var product_name = submit_btn.data('name');
        var product_price = submit_btn.data('price');
        var product_id = submit_btn.data('id');

        var data = {};
        data.product_id = product_id;
        data.nmb = nmb;
        var csrf_token = $('#form_buying_product [name="csrfmiddlewaretoken"]').val();
        data["csrfmiddlewaretoken"] = csrf_token;

        var url = form.attr('action');

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            success: function (data) {
                if (data.products_total_nmb) {
                    $('#basket_total_nmb').text("("+data.products_total_nmb+")")
                }
            },
            error: function () {
                console.log("error")
            }
        });




        $('.container .basket ul').append('<li>'+product_name+', '+nmb+' шт., по '+product_price+' RUB ' +
            '<a href="" class="delete-item">x</a>' +
            '</li>')
    });


    // Удаление из списка корзины

    $(document).on('click', '.delete-item', function (e) {
        e.preventDefault();
        $(this).closest('li').remove();
    });

});






