jQuery(function ($) {
    $(".sidebar-dropdown > a").click(function() {
        $(".sidebar-submenu").slideUp(200);
        if ($(this).parent().hasClass("active")){
            $(".sidebar-dropdown").removeClass("active");
            $(this).parent().removeClass("active");
        } else {
            $(".sidebar-dropdown").removeClass("active");
            $(this).next(".sidebar-submenu").slideDown(200);
            $(this).parent().addClass("active");
        }
    });

    $("#close-sidebar").click(function(e) {
        e.stopPropagation()
        $(".page-wrapper").toggleClass("toggled");
        $(".page-wrapper").removeClass("shows");
    });
    $("#show-sidebar").click(function(e) {
        e.stopPropagation();
        $(".page-wrapper").toggleClass("toggled");
        $(".page-wrapper").addClass("shows");
    });
});

// Close sidebar on click on body element
$(document).on("click", ".page-content", function(e){
    if($(".page-wrapper").hasClass("toggled")){
        e.stopPropagation();
        $(".page-wrapper").removeClass("shows");
    } else if($(".page-wrapper").hasClass("shows")){
        e.stopPropagation();
        $(".page-wrapper").removeClass("shows");
        $(".page-wrapper").toggleClass("toggled");
    } else {
        return false;
    }
});