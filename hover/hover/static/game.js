$(function () {
    var frame_rate = 20;
    var thrust_left = false;
    var thrust_right = false;

    window.setInterval(function () {
        $.post("/game/state",
               {"thrust_left": thrust_left,
                "thrust_right": thrust_right},
               function (response) {
                   $("#alert-not-connected").hide();
                   $("#viewer").html(response.html);
                   $("#badge-outcome-success").toggle(response.outcome === "Outcome.Success");
                   $("#badge-outcome-failure").toggle(response.outcome === "Outcome.Failure")
               })
            .fail(function() {
                $("#alert-not-connected").show();
            });
    }, 1000 / frame_rate);

    function restart() {
        $.post("/game/start");
    }

    function handlekey(e) {
        if (e.key == " " && (e.type === "keydown")) { restart(); }
        if (e.key == "c") { thrust_left = (e.type === "keydown"); }
        if (e.key == "m") { thrust_right = (e.type === "keydown"); }
    }
    $(document).keydown(handlekey).keyup(handlekey);
    restart();
});
