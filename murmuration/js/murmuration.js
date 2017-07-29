// Constants
var nBirds = 100;
var leftWing = [-10, -3];
var rightWing = [10, -3];

var initialVelocity = 20;
var dampingFactor = 0.01;
var forecastScale = 2;
var cohesionPower = 1;
var cohesionScale = 0.5;
var separationPower = -2;
var separationScale = 1e6;
var minSeparation = 1;
var alignmentScale = 1;

// Birds
var egBird = {
    position: [100, 200],
    velocity: [10, 10]
};
function moveBird(bird, dt) {
    bird.position[0] += bird.velocity[0] * dt;
    bird.position[1] += bird.velocity[1] * dt;
}
function rotate(vec, angle) {
    var cosA = Math.cos(angle);
    var sinA = Math.sin(angle);
    return [
        cosA * vec[0] - sinA * vec[1],
        sinA * vec[0] + cosA * vec[1]
    ];
}
function drawBird(bird, c) {
    c.beginPath();
    var ox = bird.position[0];
    var oy = bird.position[1];
    var a = -Math.atan2(bird.velocity[0], bird.velocity[1]);
    var left = rotate(leftWing, a);
    var right = rotate(rightWing, a);

    c.lineWidth = "3";
    c.moveTo(ox + left[0], oy + left[1]);
    c.lineTo(ox, oy);
    c.lineTo(ox + right[0], oy + right[1]);
    c.stroke();
}
function randomBirds(n, w, h) {
    var birds = [];
    for (var i = 0; i < n; ++i) {
        var orientation = Math.random() * 2 * Math.PI;
        birds.push({
            position: [
                w * Math.random(),
                h * Math.random()
            ],
            velocity: [
                initialVelocity * Math.cos(orientation),
                initialVelocity * Math.sin(orientation)
            ]
        });
    }
    return birds;
}

// Flocking
function powerLawUpdate(scale, power, minMagnitude, dx, dy, velocity) {
    var magnitude = Math.max(Math.sqrt(dx*dx + dy*dy), minMagnitude);
    var s = scale * Math.pow(magnitude, power-1);
    velocity[0] += s * dx;
    velocity[1] += s * dy;
}

function separation(bird,others,timestep) {
    others.forEach(function (otherBird) {
        if (bird != otherBird) {
            var dx = bird.position[0] - otherBird.position[0];
            var dy = bird.position[1] - otherBird.position[1];
            powerLawUpdate(separationScale * timestep / others.length, separationPower, minSeparation, dx, dy, bird.velocity);
        }
    });
}

function damping(bird, timestep) {
    var dx = bird.velocity[0];
    var dy = bird.velocity[1];
    var step = timestep * dampingFactor * Math.sqrt(dx*dx + dy*dy);
    bird.velocity[0] -= step * dx;
    bird.velocity[1] -= step * dy;
}

function cohesion(bird,others,timestep) {
    var x = 0;
    var y = 0;
    others.forEach(function (bird) {
        x += bird.position[0];
        y += bird.position[1];
    });
    x /= others.length;
    y /= others.length;
    var dx = x - bird.position[0];
    var dy = y - bird.position[1];
    powerLawUpdate(cohesionScale * timestep, cohesionPower, 0, dx, dy, bird.velocity);
}

function cohesionWithForecast(bird,others,timestep) {
    var x = 0;
    var y = 0;
    var vx = 0;
    var vy = 0;
    others.forEach(function (bird) {
        x += bird.position[0];
        vx += bird.velocity[0];
        y += bird.position[1];
        vy += bird.velocity[1];
    });
    x /= others.length;
    vx /= others.length;
    y /= others.length;
    vy /= others.length;
    var dx = x + forecastScale * vx - bird.position[0];
    var dy = y + forecastScale * vy - bird.position[1];
    powerLawUpdate(cohesionScale * timestep, cohesionPower, 0, dx, dy, bird.velocity);
}

function avoidWall(bird, width, height) {
    var x = bird.position[0];
    var y = bird.position[1];
    var xinc = bird.velocity[0];
    var yinc = bird.velocity[1];
    if((xinc<0 && x <= 0) || (xinc>0 && x >= width)) {
        bird.velocity[0] *= -1;
    }
    if((yinc<0 && y <= 0) || (yinc>0 && y >= height)) {
        bird.velocity[1] *= -1;
    }
}

function alignment(bird,others,timestep) {
    var x = 0;
    var y = 0;
    others.forEach(function (other) {
        x += other.velocity[0];
        y += other.velocity[1];
    })
    x /= others.length;
    y /= others.length;
    bird.velocity[0] += timestep * alignmentScale * x;
    bird.velocity[1] += timestep * alignmentScale * y;
}

// App
var frameRate = 30;
var birds = null;
function draw() {
    var canvas = $(".maindisplay");
    var w = canvas.width();
    var h = canvas.height();
    canvas[0].width = w;
    canvas[0].height = h;
    var c = canvas[0].getContext("2d");

    c.fillStyle = "#80A0FF";
    c.fillRect(0, 0, w, h);

    var dt = 1.0/frameRate;
    birds.forEach(function (bird) {
        cohesion(bird, birds, dt);
        separation(bird, birds, dt);
        alignment(bird, birds, dt);
        damping(bird, dt);
        avoidWall(bird, w, h);
    });
    birds.forEach(function (bird) {
        moveBird(bird, dt);
        drawBird(bird, c);
    });
}

$(function() {
    var canvas = $(".maindisplay");
    var w = canvas.width();
    var h = canvas.height();
    birds = randomBirds(nBirds, w, h);

    draw();
    window.setInterval(function () {
        draw();
    }, 1000.0 / frameRate);
});
