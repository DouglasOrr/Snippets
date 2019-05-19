$(function () {

    var timer = null;
    var thrust_left = false;
    var thrust_right = false;

    function tick() {
        $.post("/game/state",
               {"thrust_left": thrust_left, "thrust_right": thrust_right},
               function (response) {
                   $("#viewer").html(response.html);
               });
    }

    function restart() {
        $.post("/game/start", function (response) {
            var timestep = response.timestep;
            if (timer !== null) {
                window.clearInterval(timer);
            }
            timer = window.setInterval(tick, 1000 * timestep);
        });
    }

    function handlekey(e) {
        if (e.key == " " && (e.type === "keydown")) { restart(); }
        if (e.key == "c") { thrust_left = (e.type === "keydown"); }
        if (e.key == "m") { thrust_right = (e.type === "keydown"); }
    }
    $(document).keydown(handlekey).keyup(handlekey);
});
