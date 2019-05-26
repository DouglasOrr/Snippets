$(function () {
    var frame_rate = 20;
    var ticks_per_frame = 1;
    var thrust_left = false;
    var thrust_right = false;

    window.setInterval(function () {
        $.post("/game/state",
               {"thrust_left": thrust_left,
                "thrust_right": thrust_right,
                "ticks": ticks_per_frame},
               function (response) {
                   $("#viewer").html(response.html);
                   var state = response.state;
                   $("#state").text(
                       " x: " + state.x.toFixed(1) + "\n" +
                       " y: " + state.y.toFixed(1) + "\n" +
                       " a: " + state.a.toFixed(1) + "\n" +
                       "dx: " + state.dx.toFixed(1) + "\n" +
                       "dy: " + state.dy.toFixed(1) + "\n" +
                       "da: " + state.da.toFixed(1) + "\n"
                   );
               });
    }, 1000 / frame_rate);

    function restart() {
        $.post("/game/start", function (response) {
            ticks_per_frame = Math.round(1/(frame_rate * response.timestep));
        });
    }

    function handlekey(e) {
        if (e.key == " " && (e.type === "keydown")) { restart(); }
        if (e.key == "c") { thrust_left = (e.type === "keydown"); }
        if (e.key == "m") { thrust_right = (e.type === "keydown"); }
    }
    $(document).keydown(handlekey).keyup(handlekey);
});
