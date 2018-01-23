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



    // Changing button in product_item div on main page according to
    // presence product in basket
    function updateAddToBasketButtons() {
        var products_in_basket_ids = $('#hidden_basket_data').data('products-ids');
        $('.changing-button').each(function (i, elem) {
            if (products_in_basket_ids.indexOf(elem.getAttribute('data-id')) !== -1) {
                $(elem)
                    .removeClass('btn-success')
                    .addClass('btn-warning')
                    .html('В корзине! Заказать')
                    .off('click')
                    .on('click', function () {
                        window.location.pathname = 'checkout/'
                    })
            } else {
                $(elem)
                    .removeClass('btn-warning')
                    .addClass('btn-success')
                    .html('Добавить в корзину')
                    .off('click')
                    .on('click', function (e) {
                        e.preventDefault();
                        var product_id = e.target.getAttribute('data-id');
                        var data = {};
                        data.product_id = product_id;
                        updateBasketListAndAddToBasketButtons('GET', data);
                    })
            }
        })
    }


    // Updating basket list

    function updateNavbarBasket(html) {
        $('.basket-products-list').html(html);
        var hidden_data = $('#hidden_basket_data');
        $('#basket_total_nmb').text('('+hidden_data.data('total-nmb')+')');
        $('.total_price').text(hidden_data.data('total-price'));
    }


    function updateBasketListAndAddToBasketButtons(type, data) {
        $.ajax({
            url: "/basket_list/",
            type: type,
            data: data,
            cache: true,
            success: function (html) {
                updateNavbarBasket(html);
                updateAddToBasketButtons();
            },
            error: function () {
                console.log("error")
            }
        });
    }

    updateBasketListAndAddToBasketButtons();


    // Appearance of basket list div when mouseover
    $("#checkout")
        .mouseover(function () {
        $(".basket").removeClass('hidden');
        })
        .mouseout(function () {
        $(".basket").addClass('hidden')
        });
    

    // Adding to basket list on product.html
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

        updateBasketListAndAddToBasketButtons('POST', data);
    });


    // Deleting from basket list both on navbar and checkout page
    function removeFromNavbarBasketList (product_id) {
        var data = {};
        data.remove_product_id = product_id;
        updateBasketListAndAddToBasketButtons('GET', data);
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
    $('.num-products-input').on('change', function (event) {
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
                updateBasketListAndAddToBasketButtons();
            },
            error: function () {
                console.log("error")
            }
        });

    });


});