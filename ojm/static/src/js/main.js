odoo.define('ojm_script', function (require) {
    'use strict';


    $(document).ready(() => {
        if ($('#volumeSelect')) {
            $('#volumeSelect').select2();
        }
        if ($('.btn-journal')) {
            $('.btn-journal').click((ev) => {
                $('.btn-journal > .plusBtn').removeClass("bg-orange");
                var source = ev.target || ev.srcElement;
                $(source).children('.plusBtn').toggleClass("bg-orange");
            })
        }

        $(".slider_desc_toogler").on("click", function () {
            $('.slider_desc_toogler > i').toggleClass('fa-chevron-down');
            $('.slider_desc_toogler > i').toggleClass('fa-chevron-up');
            $(".caption > p").toggleClass("mini");
        });

        $(document).on('click', function(){
            $('.details').addClass('d-none');
        });

        $('.author_name').click((ev)=>{
            ev.stopPropagation();
            let source = ev.target || event.srcElement;
            let details_id = source.getAttribute('data-id');
            console.log(details_id);
            for(let i=0; i<$(".details").length; i++){
                console.log($(".details")[i]);
                let item = $(".details")[i];
                if(item.getAttribute("id") !== details_id){
                    item.classList.add('d-none');
                }
            }
            // $(".details").addClass('d-none');
            $("#"+details_id).toggleClass('d-none');
        })

        $(".article-link").click((ev) => {
            let src = ev.target || event.srcElement;;
            console.log("SRC", src);
        })

        var lazyloadImages;
        console.log("Image loading laz implementation");
        if ("IntersectionObserver" in window) {
            lazyloadImages = document.querySelectorAll(".lazy");
            var imageObserver = new IntersectionObserver(function (entries, observer) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        var image = entry.target;
                        image.src = image.dataset.src;
                        image.classList.remove("lazy");
                        imageObserver.unobserve(image);
                    }
                });
            });

            lazyloadImages.forEach(function (image) {
                imageObserver.observe(image);
            });
        } else {
            var lazyloadThrottleTimeout;
            lazyloadImages = document.querySelectorAll(".lazy");

            function lazyload() {
                if (lazyloadThrottleTimeout) {
                    clearTimeout(lazyloadThrottleTimeout);
                }

                lazyloadThrottleTimeout = setTimeout(function () {
                    var scrollTop = window.pageYOffset;
                    lazyloadImages.forEach(function (img) {
                        if (img.offsetTop < (window.innerHeight + scrollTop)) {
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                        }
                    });
                    if (lazyloadImages.length == 0) {
                        document.removeEventListener("scroll", lazyload);
                        window.removeEventListener("resize", lazyload);
                        window.removeEventListener("orientationChange", lazyload);
                    }
                }, 20);
            }

            document.addEventListener("scroll", lazyload);
            window.addEventListener("resize", lazyload);
            window.addEventListener("orientationChange", lazyload);
        }
        console.log("Image loading laz implementation");
    })

    // hide copying to clipboard button if browser if firefox
    if ($.browser.mozilla) {
        document.getElementById("ccBtn").setAttribute("style", "display:none!important");
    }
});

async function myCCFunction() {
    if (!$.browser.mozilla) {
        // permission management just works on chromium based browser, firefox decide to 
        // block it for security reasons

        // permissions setting
        const queryOpts = { name: 'clipboard-read', allowWithoutGesture: false };
        const permissionStatus = await navigator.permissions.query(queryOpts);
        // Will be 'granted', 'denied' or 'prompt':
        console.log(permissionStatus.state);
        // Listen for changes to the permission state
        permissionStatus.onchange = () => {
            console.log(permissionStatus.state);
        };

        // Get the text field
        var copyText = document.getElementById("myCitation").textContent;
        try {
            await navigator.clipboard.writeText(copyText).then(() => {
                ccBtn = document.getElementById("ccBtn");
                ccBtn.innerHTML = "Citation has been copied";
            });
        } catch (err) {
            console.error('Failed to copy: ', err);
        }
    }
}

// lazy loading implementation


