$(function() {
    var canvas = document.getElementById("main-canvas");
    var ctx = canvas.getContext("2d");
    var state = {};
    var controlLeft = false;
    var controlRight = false;
    var KEYCODE_LEFT = 37;
    var KEYCODE_RIGHT = 39;
    var DT = 0.01;

    function draw() {
        var ox = canvas.width / 2;
        var oy = canvas.height / 2;
        var radius = 20;
        var len = Math.min(ox, oy) - radius;
        var px = ox + len * Math.sin(state.theta);
        var py = oy - len * Math.cos(state.theta);

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // safe zone
        var arcstart = 3 * Math.PI / 2 - state.threshold;
        var arcend = 3 * Math.PI / 2 + state.threshold;
        ctx.strokeStyle="#30ff30";
        ctx.beginPath();
        ctx.arc(ox, oy, len / 3, arcstart, arcend);
        ctx.stroke();
        ctx.strokeStyle="#ff3030";
        ctx.beginPath();
        ctx.arc(ox, oy, len / 3, arcend, arcstart);
        ctx.stroke();

        if (state.stopped) {
            ctx.strokeStyle=ctx.fillStyle="#a00";
        } else {
            ctx.strokeStyle=ctx.fillStyle="#000";
        }
        // pendulum arm
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(ox, oy);
        ctx.lineTo(px, py);
        ctx.stroke();
        // pendulum end
        ctx.beginPath();
        ctx.arc(px, py, radius, 0, 2*Math.PI);
        ctx.fill();
    }

    function update() {
        $.post("/step", {dt: DT, control: (controlRight - controlLeft)},
               function(data) {
                   state = data;
                   $("#simulation-time")
                       .text(state.t.toFixed(2) + " s")
                       .addClass(state.stopped ? "label-danger" : "label-success")
                       .removeClass(state.stopped ? "label-success" : "label-danger");
                   if (state.manual) {
                       $("#label-manual").show();
                   } else {
                       $("#label-manual").hide();
                   }
                   $("#label-auto").text("Control: " + state.auto)
                   draw();
               });
    }

    window.setInterval(update, 1000 * DT);

    $("#restart").click(function() {
        $.post("/restart");
    });

    $(window).keydown(function(data) {
        if (data.which == KEYCODE_LEFT) {
            controlLeft = true;
        } else if (data.which == KEYCODE_RIGHT) {
            controlRight = true;
        }
    });
    $(window).keyup(function(data) {
        if (data.which == KEYCODE_LEFT) {
            controlLeft = false;
        } else if (data.which == KEYCODE_RIGHT) {
            controlRight = false;
        }
    });

    $.get("/controllers", function(data) {
        var list = [];
        $.each(data.controllers, function(i, name) {
            var elem = $("<li><a>" + name + "</a></li>").click(function () {
                $.post("/controller", {'name': name});
            });
            list.push(elem);
        });
        $("#controllers").empty().append(list);
    });
});
