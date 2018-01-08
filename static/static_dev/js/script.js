$(document).ready(function () {


    // Подсветка активного пункта меню

    var menus = [
        'main',
        'delivery',
        'contacts',
        'checkout'
    ];

    menus.forEach(function (menu) {
        if (window.location.href.indexOf(menu) !== -1){
            $('.active').removeClass('active');
            $('#' + menu).addClass('active');
        }
    });

    // if (window.location.href.indexOf('delivery') !== -1){
    //     $('.active').removeClass('active');
    //     $('#delivery').addClass('active');
    // } else if (window.location.href.indexOf('contacts') !== -1) {
    //     $('.active').removeClass('active');
    //     $('#contacts').addClass('active');
    // } else if (window.location.href.indexOf('checkout') !== -1) {
    //     $('.active').removeClass('active');
    //     $('#checkout').addClass('active');
    // } else {
    //     $('.active').removeClass('active');
    //     $('#main').addClass('active');
    // }


    // Обновление списка корзины через ajax и total_price на странице checkout

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
        $('.total_price').text(data.products_total_price)
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

    $("#checkout").mouseover(function (e) {
        $(".basket").removeClass('hidden');
    });
    $('#checkout').mouseout(function (e) {
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


    // Удаление из списка корзины одновременно в навбаре и на странице checkout

    function removeFromNavbarBasketList (product_id) {
        var data = {};
        data.remove_product_id = product_id;
        updateBasketList('GET', data);
    }

    function removeFromCheckoutBasketList (product_id) {
        $("[data-id=" + product_id + "]").remove();
    }

    $(document).on('click', '.delete-from-basket', function (e) {
        e.preventDefault();
        var product_id = $(this).attr('data-id');
        removeFromNavbarBasketList(product_id);

        if (window.location.href.indexOf('checkout') !== -1) {
            removeFromCheckoutBasketList(product_id);
        }
    });

    $('.checkout-delete-from-basket').on('click', function (e) {
        e.preventDefault();
        var product_id = $(this).closest('tr').attr('data-id');
        removeFromNavbarBasketList(product_id);
        removeFromCheckoutBasketList(product_id);
    });


    // Пересчет суммы одного товара при изменении его количества в checkout

    $('.num-products-input.checkout').on('change', function (event) {
        var product_to_change = $(this).closest('tr');
        var nmb = $(this).val();
        var product_id = product_to_change.attr('data-id');

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
                product_to_change.find('.total-product-price').text(data.total_product_price);
                updateBasketList();
            },
            error: function () {
                console.log("error")
            }
        });

    });




});