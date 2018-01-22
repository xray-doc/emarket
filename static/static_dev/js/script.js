$(document).ready(function () {


    // Highlighting active menu

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



    // Updating basket list

    function updateNavbarBasket(data) {
        if (data.products_total_nmb) {
            $('#basket_total_nmb').text("("+data.products_total_nmb+")");
            $('.basket-products-list').html("");
            $.each(data.products, function (k, v) {
                $('.basket-products-list').append(
                    '<div class="product-in-basket" >' +
                        v.name+ ', <strong>(' + v.nmb + ' шт.)</strong>'+
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



    // Appearance of basket list div when mouseover

     
    $("#checkout")
        .mouseover(function () {
        $(".basket").removeClass('hidden');
        })
        .mouseout(function () {
        $(".basket").addClass('hidden')
        });
    

    // Adding to basket list

        // On product.html
    $('#form_buying_product').on('submit', function (e) {
        e.preventDefault();

        var form = $('#form_buying_product');
        var nmb = $('.num-products-input').val();
        var submit_btn = $('#submit-btn');
        var product_id = submit_btn.data('id');
        var csrf_token = form.find('[name="csrfmiddlewaretoken"]').val();
        var data = {};

        data.product_id = product_id;
        data.nmb = nmb;
        data["csrfmiddlewaretoken"] = csrf_token;

        updateBasketList('POST', data);
    });

        // On main page
    $('.add-to-cart-btn .btn-success').on('click', function (e) {
        e.preventDefault();
        var product_id = e.target.getAttribute('data-id');
        var data = {};
        data.product_id = product_id;
        updateBasketList('GET', data);

        // Changing button to checkout link
        $(this)
            .removeClass('btn-success')
            .addClass('btn-warning')
            .off('click')
            .on('click', function () {
               window.location.pathname = 'checkout/'
            })
            .html('Оформить заказ')

    });


    // Deleting from basket list both on navbar and checkout page

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


    // Updating total_price when changing on checkout page

    $('.num-products-input.checkout').on('change', function (event) {
        var product_to_change = $(this).closest('tr');
        var nmb = $(this).val();
        var product_id = product_to_change.attr('data-id');

        var data = {};
        data["csrfmiddlewaretoken"] =  $('#form_change_product').find('[name="csrfmiddlewaretoken"]').val();
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