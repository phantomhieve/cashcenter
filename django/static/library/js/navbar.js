$(document).ready(function () {
  // Navbar toggler icon transition
  $('.navbar-collapse').on('show.bs.collapse', function () {
    var icon = $('.navbar-toggler-icon i');
    icon.css('opacity', '0');
    setTimeout(function () {
      icon.removeClass('fa-navicon').addClass('fa-times');
      icon.css('opacity', '1');
    }, 150); // Wait for half the transition
  });
  $('.navbar-collapse').on('hide.bs.collapse', function () {
    var icon = $('.navbar-toggler-icon i');
    icon.css('opacity', '0');
    setTimeout(function () {
      icon.removeClass('fa-times').addClass('fa-navicon');
      icon.css('opacity', '1');
    }, 150);
  });
});
