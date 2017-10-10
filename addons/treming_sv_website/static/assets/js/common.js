/*var _cit = (function() {
    'use strict';

    var baseUrl;

    var initNewsLetterForm = function() {
        $('#nl_msg').validate({
            rules: {
                newsletter_email: {
                    required: true,
                    email: true
                }
            }
        });
        $('#newsletter_signup').on('click', function () {
            if ($('#nl_msg').valid()) {
                $("#myModal").modal("show");
                return;
            } else {
                return;
            }
        });
        $('#captchaSubmit').on('click', function () {
            $("#myModal").modal("hide");
            $('#loader').removeClass('hidden');
            $('#nl_msg').addClass('hidden');
            $.ajax({
                type: "POST",
                url: baseUrl + '/newsLetter',
                data: 'newsletter_email=' + $('#newsletter_email').val() + '&g-recaptcha-response=' + $("#g-recaptcha-response").val(),
                dataType: 'json',
                success: function (response) {
                    $('#loader').addClass('hidden');
                    $('#nl_msg').removeClass();
                    if (response.status == 'success') {
                        $("#captchaMessage").html('<span class="sub-alert-success">' + response.message + '</span>');
                        return false;
                    } else if (response.status == 'error') {
                        $("#captchaMessage").html('<span class="sub-alert-error">' + response.message + '</span>');
                        return false;
                    }
                    $("#captchaMessage").html('<span class="sub-alert-error">' + response.newsLetterCaptcha[0] + '</span>');
                }
            });
        });
    };

    var warnOnPageLeave = function(e) {
        if (!e)
            e = window.event;
        //e.cancelBubble is supported by IE - this will kill the bubbling process.
        e.cancelBubble = true;
        e.returnValue = 'You sure you want to leave?'; //This is displayed on the dialog

        //e.stopPropagation works in Firefox.
        if (e.stopPropagation) {
            e.stopPropagation();
            e.preventDefault();
        }
    };

    var odooManager = (function() {

        var signupValidator;

        /**
         * Function to Create Odoo Trial Database
         * @param {type} mailCode
         * @author Hari
         *//*
        var createOdooTrial = function(mailCode) {
            window.onbeforeunload = warnOnPageLeave;
            $('#loader').removeClass('hidden');
            $.ajax({
                type: "POST",
                url: baseUrl + '/odoo-trial/createOdooTrialDB',
                data: 'code=' + mailCode,
                success: function (response) {
                    var result = $.parseJSON(response);
                    $('#loader').addClass('hidden');
                    $('#success_message').removeClass('hidden');
                    $('#success_message').html(result.message);
                    window.onbeforeunload = "";
                }
            });
        };

        var handleSubmitError = function(response) {
            if (!response.success) {
                if (response.errors) {
                    var errors = {};
                    for(var i in response.errors) {
                        errors[i] = response.errors[i][0]
                    };
                    signupValidator.showErrors(errors);
                }
            }
        };

        var initSignup = function () {
            var signUpForm = $('#odoo_signup_form');
            if (signUpForm.length > 0) {

                $('[name=no_of_users]').on('change', function() {
                    var noOfUsers = parseInt($(this).val());
                    var price = noOfUsers * parseInt($(this).data('price'));
                    var container = $(this).closest('.package-col').find('.offer-round');
                    container.find('h4').text('$' + price);
                    container.find('.no_of_users').text(noOfUsers);
                });

                $('[name=no_of_users]').change();

                $('.odooSignup').on('click', function() {
                    $('body').addClass('popup-modal-active');
                    $('.popup-fixed-frame, .popup-black-overlay').show();
                    var type = $(this).data('type');

                    if (type == 'trail') {
                        signUpForm.find('[name=password]').show();
                        signUpForm.find('[name=password_confirmation]').show();
                    } else {
                        signUpForm.find('[name=password]').hide();
                        signUpForm.find('[name=password_confirmation]').hide();
                    }
                    signUpForm.find('[name=type]').val($(this).data('type'));
                    signUpForm.find('[name=no_of_users]').val($(this).closest('.package-col').find('select[name=no_of_users]').val());

                });

                $(document).on('click.popup', function(e) {
                    var elems = $('.popup-container,.odooSignup');
                    if ($(e.target).is('.popup-close') || (!elems.is(e.target) && elems.has(e.target).length === 0)) {
                        $('body').removeClass('popup-modal-active');
                        $('.popup-fixed-frame, .popup-black-overlay').hide();
                        signupValidator.resetForm();
                    }
                });

                signupValidator = signUpForm.validate({
                    rules: {
                        email: {
                            required: true,
                            email: true
                        },
                        company: {
                            required: true
                        },
                        name: {
                            required: true
                        },
                        phone: {
                            required: true
                        },
                        password: {
                            required: true
                        },
                        password_confirmation: {
                            required: true,
                            equalTo : "[name=password]"
                        }
                    }
                });

                $('#submit_signup').on('click', function(e) {
                    e.preventDefault();
                    if ($('#odoo_signup_form').valid()) {
                        $.ajax({
                            url: baseUrl + '/odoo-signup',
                            type: 'post',
                            data: $('#odoo_signup_form').serialize(),
                            dataType: 'json',
                            success: function(response) {
                                if (response && response.success) {
                                    $('#odoo_signup_form').hide();
                                    $('#odoo_signup_success').show();
                                    return;
                                }
                                handleSubmitError(response)
                            },
                            failure: handleSubmitError
                        });
                    }
                });
            }
        };

        return {
            createOdooTrial: createOdooTrial,
            initSignup: initSignup
        };


    })();

    var fixHeaderOnScroll = function() {
        if ($(window).scrollTop() > 1) {
            $('header').addClass('negative_head');
        } else {
            $('header').removeClass('negative_head');
        }

        var odooSection = $('.odoo-section');
        if (odooSection.length > 0) {
            if ($(window).scrollTop() + $(window).height() / 2.5 > odooSection.offset().top) {
                $('#cn-button,#cn-wrapper,#curver-outline').addClass('opened-nav');
            }
        }
    };

    var init = function(config) {
        baseUrl = config.baseUrl;
        initNewsLetterForm();
        $(window).scroll(fixHeaderOnScroll);

        $('#enquiry_form').validate();

        $('a.ceo-read').click(function() {
            $(this).hide();
            $('.short_desc').hide();
            $('.full_desc').show();
        });
        
        $('#slider1').bxSlider({
            mode: 'fade',
            auto: true,
            autoControls: true,
            pause: 5000
        });
        
        $('.bxslider').bxSlider();

        odooManager.initSignup();
    };

    return {
        init: init,
        odooManager: odooManager
    };
    

})();*/