
(function ($) {//jQuery to collapse the navbar on scroll
    $(window).scroll(function() {

    if ($(window).scrollTop() > 50) {
            $('header').addClass('negative_head');
            $("footer").css({"display": "block"});
        } else {
            $('header').removeClass('negative_head');
            $("footer").css({"display": "none"});
        }


        var top = $("footer").outerHeight(true)  ;

        $("main").css({"margin-bottom": top + "px"});





    });
    
})(jQuery);






$(document).ready(function(){
    
    /**
     * Esta función calcula la edad de una persona y los meses
     * La fecha la tiene que tener el formato yyyy-mm-dd que es
     * metodo que por defecto lo devuelve el <input type="date">
     */

    var dia = 12;
    var mes = 4;
    var ano = 2009;

    // cogemos los valores actuales
    var fecha_hoy = new Date();
    var ahora_ano = fecha_hoy.getYear();
    var ahora_mes = fecha_hoy.getMonth()+1;
    var ahora_dia = fecha_hoy.getDate();

    // realizamos el calculo
    var edad = (ahora_ano + 1900) - ano;
    if ( ahora_mes < mes )
    {
        edad--;
    }
    if ((mes == ahora_mes) && (ahora_dia < dia))
    {
        edad--;
    }
    if (edad > 1900)
    {
        edad -= 1900;
    }

    // calculamos los meses
    var meses=0;
    if(ahora_mes>mes)
        meses=ahora_mes-mes;
    if(ahora_mes<mes)
        meses=12-(mes-ahora_mes);
    if(ahora_mes==mes && dia>ahora_dia)
        meses=11;

    // calculamos los dias
    var dias=0;
    if(ahora_dia>dia)
        dias=ahora_dia-dia;
    if(ahora_dia<dia)
    {
        ultimoDiaMes=new Date(ahora_ano, ahora_mes, 0);
        dias=ultimoDiaMes.getDate()-(dia-ahora_dia);
    }

    $("#dad").text(edad);
    $("#dad-2").text(edad);
    $("#dad-3").text(edad);

    $("#dad-i").text(edad);
    $("#dad-a").text(edad);
    $("#dad-f").text(edad);
    $("#dad-b").text(edad);






        var anio = (new Date).getFullYear();
        $("#ahocopy").text(anio);





    $(document).on("click",".has-child",function(e){
        var state='';
        if(!$(this).hasClass("open"))
            state='open';
        $(".has-child").removeClass("open");
        $(this).addClass(state);
    });


    $(document).on("click",".car-list",function(e){





            if($(this).hasClass("car-list-sh"))
            $(this).removeClass("car-list-sh");
            else
            $(this).addClass("car-list-sh");



    });



});

$(document).ready(function(){
    $('.bxslider').bxSlider();

    $('#slider1').bxSlider({
        mode: 'fade',
        auto: true,
        autoControls: true,
        pause: 5000
    });

});

$(document).ready(function () {
    (
        function () {
            $('.slider').anyslider({
                animation: 'slide',
                interval: 4000,
                showControls: true,
                pauseOnHover: true
            });

            $('.slider1').anyslider({
                animation: 'slide',
                interval: 4000,
                showControls: true,
                pauseOnHover: true
            });

            $('.slider-video').anyslider({
                animation: 'slide',
                interval: 5000,
                showControls: true,
                pauseOnHover: true
            });





            $('.count').each(function () {
                $(this).prop('Counter',0).animate({
                    Counter: $(this).text()
                }, {
                    duration: 4000,
                    easing: 'swing',
                    step: function (now) {
                        $(this).text(Math.ceil(now));
                    }
                });
            });


        })(jQuery);
});

