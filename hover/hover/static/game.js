$(function () {
    var frame_rate = 20;
    var thrust_left = false;
    var thrust_right = false;

    window.setInterval(function () {
        $.post("/game/state",
               {"thrust_left": thrust_left,
                "thrust_right": thrust_right},
               function (response) {
                   $("#viewer").html(response.html);
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
