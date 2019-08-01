function recalculate_odds() {
    $.get("/odds?" + $.param({"attack": $("#attack").val(),
                              "defend": $("#defend").val()}),
          function (response) {
              var expect_win = response.attacker_win_probability > 0.5;
              $("#outcome")
                  .text("Win: " + (100 * response.attacker_win_probability).toFixed(1) + "%")
                  .addClass(expect_win ? "badge-success" : "badge-danger")
                  .removeClass(expect_win ? "badge-danger" : "badge-success");
          });
}

$(function() {
    $("#attack").change(recalculate_odds);
    $("#defend").change(recalculate_odds);
    recalculate_odds();
});
