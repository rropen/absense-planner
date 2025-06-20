// For Bulma's "notification" and "delete" elements
$(".delete").on("click", function () {
  let element_to_be_hidden = $(this).parent();
  element_to_be_hidden.addClass("is-hidden");
});
