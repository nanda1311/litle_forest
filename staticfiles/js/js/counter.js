(function ($) {
    "use strict";
    $.fn.counterUp = function (options) {
        var settings = $.extend({ time: 400, delay: 10, offset: 100, beginAt: 0, formatter: false, context: "window", callback: function () {} }, options),
            s;
        return this.each(function () {
            var $this = $(this),
                counter = {
                    time: $(this).data("counterup-time") || settings.time,
                    delay: $(this).data("counterup-delay") || settings.delay,
                    offset: $(this).data("counterup-offset") || settings.offset,
                    beginAt: $(this).data("counterup-beginat") || settings.beginAt,
                    context: $(this).data("counterup-context") || settings.context,
                };
            var counterUpper = function () {
                var nums = [];
                var divisions = counter.time / counter.delay;
                var num = $(this).attr("data-num") ? $(this).attr("data-num") : $this.text();
                var isComma = /[0-9]+,[0-9]+/.test(num);
                num = num.replace(/,/g, "");
                var decimalPlaces = (num.split(".")[1] || []).length;
                if (counter.beginAt > num) counter.beginAt = num;
                var isTime = /[0-9]+:[0-9]+:[0-9]+/.test(num);
                if (isTime) {
                    var times = num.split(":"),
                        m = 1;
                    s = 0;
                    while (times.length > 0) {
                        s += m * parseInt(times.pop(), 10);
                        m *= 60;
                    }
                }
                for (var i = divisions; i >= (counter.beginAt / num) * divisions; i--) {
                    var newNum = parseFloat((num / divisions) * i).toFixed(decimalPlaces);
                    if (isTime) {
                        newNum = parseInt((s / divisions) * i);
                        var hours = parseInt(newNum / 3600) % 24;
                        var minutes = parseInt(newNum / 60) % 60;
                        var seconds = parseInt(newNum % 60, 10);
                        newNum = (hours < 10 ? "0" + hours : hours) + ":" + (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds < 10 ? "0" + seconds : seconds);
                    }
                    if (isComma) {
                        while (/(\d+)(\d{3})/.test(newNum.toString())) {
                            newNum = newNum.toString().replace(/(\d+)(\d{3})/, "$1" + "," + "$2");
                        }
                    }
                    if (settings.formatter) {
                        newNum = settings.formatter.call(this, newNum);
                    }
                    nums.unshift(newNum);
                }
                $this.data("counterup-nums", nums);
                $this.text(counter.beginAt);
                var f = function () {
                    if (!$this.data("counterup-nums")) {
                        settings.callback.call(this);
                        return;
                    }
                    $this.html($this.data("counterup-nums").shift());
                    if ($this.data("counterup-nums").length) {
                        setTimeout($this.data("counterup-func"), counter.delay);
                    } else {
                        $this.data("counterup-nums", null);
                        $this.data("counterup-func", null);
                        settings.callback.call(this);
                    }
                };
                $this.data("counterup-func", f);
                setTimeout($this.data("counterup-func"), counter.delay);
            };
            $this.waypoint(
                function (direction) {
                    counterUpper();
                    this.destroy();
                },
                { offset: counter.offset + "%", context: counter.context }
            );
        });
    };
})(jQuery);
(function($) {
    /* Gallery Isotope */
    function GalleryIsotope() {
        if ($('.gallery').length) {
            $('.gallery').each(function(index, el) {
                var $this = $(this),
                    $isotope = $this.find('.gallery-isotope'),
                    $filter = $this.find('.gallery-cat');

                if ($isotope.length) {
                    var isotope_run = function(filter) {
                        $isotope.isotope({
                            itemSelector: '.item-isotope',
                            filter: filter,
                            percentPosition: true,
                            masonry: {
                                columnWidth: '.item-size'
                            },
                            transitionDuration: '0.6s',
                            hiddenStyle: {
                                opacity: 0
                            },
                            visibleStyle: {
                                opacity: 1
                            }
                        });
                    }

                    $filter.on('click', 'a', function(event) {
                        event.preventDefault();
                        $(this).parents('ul').find('.active').removeClass('active');
                        $(this).parent('li').addClass('active');
                        isotope_run($(this).attr('data-filter'));
                    });

                    isotope_run('*');
                }
            });
        }
    }

    $(window).load(function() {
        $('#preloader').delay(1000).fadeOut('400', function() {
            $(this).fadeOut()
        });
        $('body').append('<div class="awe-popup-overlay" id="awe-popup-overlay"></div><div class="awe-popup-wrap" id="awe-popup-wrap"><div class="awe-popup-content"></div><span class="awe-popup-close" id="awe-popup-close"></div>');
        GalleryIsotope();
    });

})(jQuery);

// Open Fullscreen Image Modal
function openFullscreen() {
    var modal = document.getElementById("fullscreen-modal");
    var img = document.querySelector(".product-image"); // Change this to your main image
    var fullscreenImage = document.getElementById("fullscreen-image");

    fullscreenImage.src = img.src; // Set the clicked image to the fullscreen modal
    modal.style.display = "flex";
}

// Close Fullscreen Image Modal
function closeFullscreen() {
    var modal = document.getElementById("fullscreen-modal");
    modal.style.display = "none";
}

// Handle Quickview Modal
document.querySelectorAll('.quickview-btn').forEach(button => {
    button.addEventListener('click', function () {
        const modal = document.querySelector('#quickview');
        const productImage = this.closest('.product-card').querySelector('.main-img').src;
        const modalImage = modal.querySelector('.modal-body img');
        modalImage.src = productImage;
    });
});

// Handle Add to Cart Modal (if using Bootstrap Modal)
document.querySelectorAll('.cart-btn').forEach(button => {
    button.addEventListener('click', function () {
        const modal = document.querySelector('#add-to-cart');
        const productName = this.closest('.product-card').querySelector('.product-title h6').innerText;
        const modalTitle = modal.querySelector('.modal-title');
        modalTitle.innerText = `Added ${productName} to Cart`;
    });
});
