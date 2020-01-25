$(document).ready(function () {


    // Highlighting active menu
    var menus = [
        'main',
        'delivery',
        'contacts',
        'checkout',
        'login',
        'register'
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
                    .html('Added! Checkout')
            } else {
                $(elem)
                    .removeClass('btn-info btn-go-to-checkout')
                    .addClass('btn-success btn-add-to-basket')
                    .html('Add to basket')
            }
        })
    }

    $(document)
        .on('click', '.btn-add-to-basket', function (e) {
            if (e.target.getAttribute('id') != 'submit-btn') {         // because we don't need this logic
                var product_id = e.target.getAttribute('data-id');     // when submit button in form clicked
                var data = {};                                         // (on products.html)
                data.product_id = product_id;
                data.csrfmiddlewaretoken = document.querySelector('[name="csrfmiddlewaretoken"]').value
                updateBasketList('POST', data);
            }
            navbarBasketAppearance();
        })
        .on('click', '.btn-go-to-checkout', function (e) {
            window.location.pathname = 'orders/checkout/';
        })


    // MOBILE DEVICES. Showing and hiding menu.
    $('#menu-btn').click(function () {
        $(this).toggleClass('btn-secondary btn-danger');
        var display = $('#navbar li:not(#checkout)').css('display');
        var newdisplay = (display == 'none') ? 'block' : 'none';
        $('#navbar li:not(#checkout)').css('display', newdisplay);

        if (newdisplay == 'block') {
            $('.navbar-collapse').css('height', 'auto');
        } else {
            $('.navbar-collapse').css('height', '0');
        }
    })


    // Short appearance of basket when product added
    var basket_appearance_timerId = 0;
    function navbarBasketAppearance() {
        $('.basket').show(duration=400);
        clearTimeout(basket_appearance_timerId)
        basket_appearance_timerId = setTimeout(function () {
            $('.basket').hide(duration = 400);
            basket_appearance_timerId = 0;
        }, 2000)
    }


    // Updating basket list
    function updateNavbarBasket(html) {
        $('.basket-products-list').html(html);
        var hidden_data = $('#hidden_basket_data');
        $('#basket_total_nmb').text('('+hidden_data.data('total-nmb')+')');
        $('.total_price').text(hidden_data.data('total-price'));
    }


    function updateBasketList(type, data) {
        $.ajax({
            url: "/orders/update_basket_list/",
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

    updateBasketList();


    // Appearance of navbar basket list when mouseover
    $("#checkout")
        .mouseover(function () {
            if (basket_appearance_timerId != 0) {           // basket list could be already showing if user
                clearTimeout(basket_appearance_timerId);    // added a product to basket recently.
                basket_appearance_timerId = 0;              // In that case basket list appears and
            } else {                                        // a timer started to hide basket list after a second.
                $(".basket").show();
            }
        })
        .mouseout(function () {
            $(".basket").hide();
        });
    

    // Adding to basket list on product_detail.html
    $('#form_buying_product').on('submit', function (e) {
        e.preventDefault();

        var submit_btn = $('#submit-btn');
        if (submit_btn.hasClass('btn-go-to-checkout')){
            // Because if product is already in basket
            // and button class have changed to "btn-go-to-basket",
            // we don't need to add this product to basket
            // again, we only need to redirect to checkout.
            // so the function should stop.
            return false;
        }

        var form = $(this);
        var nmb = $('.product-nmb-form').val();
        var product_id = submit_btn.data('id');
        var csrf_token = form.find('[name="csrfmiddlewaretoken"]').val();
        var data = {};

        data.product_id = product_id;
        data.nmb = nmb;
        data["csrfmiddlewaretoken"] = csrf_token;

        updateBasketList('POST', data);
    });

    
    // Appearance of reply to comment form on prodcut page
    $('.comment-reply-btn').click(function (e) {
        e.preventDefault();
        var parent = $(e.target).closest('blockquote');
        var comment_form = $(parent).find('.comment-reply-form')
        comment_form.fadeToggle();
    })
    

    // Deleting from basket list both on navbar and checkout page
    function removeFromNavbarBasketList (product_id) {
        var data = {};
        data.remove_product_id = product_id;
        data.csrfmiddlewaretoken = document.querySelector('[name="csrfmiddlewaretoken"]').value
        updateBasketList('POST', data);
    }

    function removeFromCheckoutBasketList (product_id) {
        $("[data-id=" + product_id + "]").hide(duration=300);
    }

    $(document)
        .on('click', '.delete-from-basket', function (e) {
            var product_id = $(this).attr('data-id');
            $(e.target).closest('.product-in-basket').hide(duration=300, complete=function () {
                removeFromNavbarBasketList(product_id);
            })
            // var product_id = $(this).attr('data-id');
            // removeFromNavbarBasketList(product_id);
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
                url: "/orders/change_product_quantity/",
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
            })
        })


    // Filter logic:
    // renewing product items on main page when filter used
    function filterProduct (form) {
        var filteredProductsUrl = "/filtered_products/";
        if (form.serialize().length == 0) {
            return False;
        }
        $.ajax({
            method: "POST",
            data: form.serialize(),
            url: filteredProductsUrl,
            success: function(html){
              $("#product_items").html(html);
              updateAddToBasketButtons();
            },
            error: function(data){
                console.log('Fail to receive filtered products from server')
            }
        })
    }

    $('.filter-form').change(function (e) {
        e.preventDefault();
        filterProduct($(this));
    })

    $('#reset_btn').click(function (e) {
        $('.filter-form').trigger('reset');
        $('.filter-form').change();
    })

    // Here default submit action prevented when search button is clicked
    // (because we use AJAX in filterProduct func)
    $('#search_button').click(function (e) {
        // $('.filter-form').change();
        e.preventDefault();
        filterProduct($(this));
    })


});