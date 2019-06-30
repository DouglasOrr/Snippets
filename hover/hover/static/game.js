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
                   var state = response.ship_state;
                   $("#state").text(
                       // See hover_game.State.Ship
                       " x: " + state[0].toFixed(1) + "\n" +
                       " y: " + state[1].toFixed(1) + "\n" +
                       " a: " + state[2].toFixed(1) + "\n" +
                       "dx: " + state[3].toFixed(1) + "\n" +
                       "dy: " + state[4].toFixed(1) + "\n" +
                       "da: " + state[5].toFixed(1) + "\n"
                   );
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
