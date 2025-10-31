$(document).ready(function () {
  // when the modal is shown
  $("#deleteConfirmModal").on("show.bs.modal", function (event) {
    const button = $(event.relatedTarget);
    const contactId = button.data("id");
    const deleteUrl = button.data("url");
    $("#modal-contact-id").text(contactId);
    // set the delete url
    $("#confirmDeleteBtn").attr("href", deleteUrl);
  });
  // when the delete button is clicked
  $("#confirmDeleteBtn").click(function (event) {
    // close the modal
    $("#deleteConfirmModal").modal("hide");
    setTimeout(() => {
      window.location.href = $("#confirmDeleteBtn").attr("href");
    }, 300);
  });
});
