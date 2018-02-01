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

        // when django renders template of products in navbar basket,
        // it includes hidden data with ids of all products in basket
        var products_in_basket_ids = $('#hidden_basket_data').data('products-ids');

        // If product's id on product_item_div matches with one of those that is already in basket,
        // its button in product_item div changes from "add to basket" to "go to checkout"
        // else - "add to basket"
        $('.changing-button').each(function (i, elem) {
            if (products_in_basket_ids.indexOf(elem.getAttribute('data-id')) !== -1) {
                $(elem)
                    .removeClass('btn-success btn-add-to-basket')
                    .addClass('btn-info btn-go-to-checkout')
                    .html('В корзине! Заказать')
            } else {
                $(elem)
                    .removeClass('btn-info btn-go-to-checkout')
                    .addClass('btn-success btn-add-to-basket')
                    .html('Добавить в корзину')
            }
        })
    }

    $(document)
        .on('click', '.btn-add-to-basket', function (e) {
            var product_id = e.target.getAttribute('data-id');
            var data = {};
            data.product_id = product_id;
            updateBasketListAndAddToBasketButtons('GET', data);
            navbarBasketAppearance();
        })
        .on('click', '.btn-go-to-checkout', function (e) {
            window.location.pathname = 'checkout/';
        })



    // Short appearance of basket when product added
    function navbarBasketAppearance() {
        $('.basket').removeClass('hidden');
        setTimeout(function () {
            $('.basket').addClass('hidden');
        }, 1250)
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

    $(document)
        .on('click', '.delete-from-basket', function (e) {
            var product_id = $(this).attr('data-id');
            removeFromNavbarBasketList(product_id);
            if (window.location.href.indexOf('checkout') !== -1) {
                removeFromCheckoutBasketList(product_id);
            }
        })
        .on('click', '.checkout-delete-from-basket', function (e) {
            var product_id = $(this).closest('tr').attr('data-id');
            removeFromNavbarBasketList(product_id);
            removeFromCheckoutBasketList(product_id);
        })
        .on('change', '.num-products-input', function (event) {
            var product_id = $(event.target).attr('data-id');
            var product_to_change = $('tr[data-id=' +product_id + ']'); // product in table row on checkout page
            var nmb = $(event.target).val();

            // If product nmb changed through navbar basket list while user on checkout page,
            // this command updates nmb value in checkout products table:
            product_to_change.find('.num-products-input').val(nmb);

            var data = {};
            data["csrfmiddlewaretoken"] =  $('.form-change-product').find('[name="csrfmiddlewaretoken"]').val();
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
            })
        })


    // Filter logic:
    // renewing product items on main page when filter used
    $('.filter-form').change(function (e) {
        e.preventDefault()
        var url_filteredProducts = "/filtered_products/";
        $.ajax({
            method: "POST",
            data: $(this).serialize(),
            url: url_filteredProducts,
            success: function(html){
              $("#product_items").html(html);
              updateAddToBasketButtons();
            },
            error: function(data){
                console.log('error')
            }
        })
    })

});