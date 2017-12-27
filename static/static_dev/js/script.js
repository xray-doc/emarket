$(document).ready(function () {


    // Список корзины

    function updateBasketList(type, data) {
        $.ajax({
            url: "/basket_list/",
            type: type,
            data: data,
            cache: true,
            success: function (data) {
                if (data.products_total_nmb) {
                    $('#basket_total_nmb').text("("+data.products_total_nmb+")")
                    $('.basket-products-list').html("");
                    $.each(data.products, function (k, v) {
                        $('.basket-products-list').append(
                            '<div class="product-in-basket" >' +v.name+ ', ' +v.nmb+ ' шт. '+
                                '<div class="delete-button" data-id='+v.id+'>X</div>' +
                            '</div>'
                        );
                    });
                } else {
                    $('#basket_total_nmb').text("");
                    $('.basket-products-list').html(
                        '<div class="product-in-basket" id="empty-basket"> Корзина пуста! </div>'
                    );
                }
                $('#basket-summ').text("Сумма: " +data.products_total_price+ " руб")
            },
            error: function () {
                console.log("error")
            }
        });
    }

    updateBasketList('GET');


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
        var product_id = submit_btn.data('id');
        var csrf_token = $('#form_buying_product [name="csrfmiddlewaretoken"]').val();
        var data = {};

        data.product_id = product_id;
        data.nmb = nmb;
        data["csrfmiddlewaretoken"] = csrf_token;

        updateBasketList('POST', data);
    });


    // Удаление из списка корзины

    $(document).on('click', '.delete-button', function (e) {
        e.preventDefault();

        var product_in_basket_id = $(this).attr('data-id');
        var data = {};

        data.remove_product_id = product_in_basket_id;
        updateBasketList('GET', data);
    });


});