$(document).ready(function () {


    // Обновление списка корзины через ajax

    function updateNavbarBasket(data) {
        if (data.products_total_nmb) {
            $('#basket_total_nmb').text("("+data.products_total_nmb+")")
            $('.basket-products-list').html("");
            $.each(data.products, function (k, v) {
                $('.basket-products-list').append(
                    '<div class="product-in-basket" >' +v.name+ ', ' +v.nmb+ ' шт. '+
                        '<button type="button" class="close delete-from-basket"' +
                        'data-id=' +v.id+ ' aria-label="Close">' +
                        '<span aria-hidden="true">&times;</span> </button>' +
                    '</div>'
                );
            });
        } else {
            $('#basket_total_nmb').text("");
            $('.basket-products-list').html(
                '<div class="product-in-basket" id="empty-basket"> Корзина пуста! </div>'
            );
        }
        $('#total_price').text(data.products_total_price)
    }


    function updateBasketList(type, data) {
        $.ajax({
            url: "/basket_list/",
            type: type,
            data: data,
            cache: true,
            success: function (data) {
                updateNavbarBasket(data);
            },
            error: function () {
                console.log("error")
            }
        });
    }



    // Появление списка корзины при наведении на кнопку "Корзина"

    $("#basket-btn").mouseover(function (e) {
        $(".basket").removeClass('hidden');
    });
    $('#basket-btn').mouseout(function (e) {
        $(".basket").addClass('hidden')
    });



    // Добавление товара в список при нажатии кнопки "Добавить в корзину"

        // На странице товара
    $('#form_buying_product').on('submit', function (e) {
        e.preventDefault();

        var form = $('#form_buying_product');
        var nmb = $('.num-products-input').val();
        var submit_btn = $('#submit-btn');
        var product_id = submit_btn.data('id');
        var csrf_token = $('#form_buying_product [name="csrfmiddlewaretoken"]').val();
        var data = {};

        data.product_id = product_id;
        data.nmb = nmb;
        data["csrfmiddlewaretoken"] = csrf_token;

        updateBasketList('POST', data);
    });

        // На главной странице
    $('.add-to-cart-btn .btn-success').on('click', function (e) {
        e.preventDefault();
        var product_id = e.target.getAttribute('data-id');
        var data = {};
        data.product_id = product_id;
        updateBasketList('GET', data);
    });


    // Удаление из списка корзины

    function removeFromBasket(product_id) {
        var data = {};
        data.remove_product_id = product_id;
        updateBasketList('GET', data);
    }

    $(document).on('click', '.delete-from-basket', function (e) {
        e.preventDefault();
        var product_id = $(this).attr('data-id');
        removeFromBasket(product_id);
    });

    $('.product-price').on('click', function (e) {
        e.preventDefault();
        var parent = $(this).closest('tr');
        var product_id = parent.attr('data-id');
        parent.remove();
        removeFromBasket(product_id);
    });


    // Подсветка активного пункта меню

    if (window.location.href.indexOf('delivery') !== -1){
        $('.active').removeClass('active');
        $('#delivery').addClass('active');
    } else if (window.location.href.indexOf('contacts') !== -1) {
        $('.active').removeClass('active');
        $('#contacts').addClass('active');
    } else {
        $('.active').removeClass('active');
        $('#main').addClass('active');
    }


    // Пересчет суммы при изменении количества товара в checkout

    $('.num-products-input.checkout').on('change', function (event) {
        var parent = $(this).closest('tr');
        var nmb = $(this).val();
        var product_id = parent.attr('data-id');

        var data = {};
        data["csrfmiddlewaretoken"] =  $('#form_change_product [name="csrfmiddlewaretoken"]').val();
        data.nmb = nmb;
        data.product_id = product_id;

        $.ajax({
            url: "/changeBasket/",
            type: "POST",
            data: data,
            cache: true,
            success: function (data) {
                parent.find('.total-product-price').text(data.product_total_price)
                updateBasketList()
            },
            error: function () {
                console.log("error")
            }
        });
    });




});