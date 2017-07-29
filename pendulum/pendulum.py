import math

class Simulation:
    """Runs a simple inverted pendulum simulation."""
    def __init__(self, noise):
        """Noise should be callable with the current time, return the torque."""
        # constants
        self.mom_mass_1 = 0.1
        self.mom_mass_2 = 1.0
        self.damping = 0.01
        self.dt = 1.0 / 1000
        self.noise = noise
        self.max_controller_torque = 10
        self.g = 10.0
        # simulation variables
        self.t = 0.0
        self.theta = 0.0
        self.dtheta_dt = 0.0

    def step(self, controller):
        """Advance the simulation by a single timestep.
        Controller should be callable, and return the torque."""
        # calculate
        c = controller(self.theta, self.dtheta_dt, self.mom_mass_1, self.mom_mass_2, self.g, self.dt)
        controller_torque = min(self.max_controller_torque, max(-self.max_controller_torque, c))
        noise_torque = self.noise(self.t)
        gravity_torque = self.g * self.mom_mass_1 * math.sin(self.theta)
        damping_torque = -self.damping * self.dtheta_dt
        d2theta_dt2 = (controller_torque + noise_torque + gravity_torque + damping_torque) / self.mom_mass_2
        # update
        self.theta += self.dtheta_dt * self.dt / 2
        self.dtheta_dt += d2theta_dt2 * self.dt
        self.theta += self.dtheta_dt * self.dt / 2
        self.theta = (self.theta + math.pi) % (2*math.pi) - math.pi
        self.t += self.dt

class ManualControl:
    def __init__(self, constant, auto_control):
        self.constant = constant
        self.auto_control = auto_control
        self.control = 0
    def __call__(self, theta, dtheta_dt, mom_mass_1, mom_mass_2, g, dt):
        return (self.constant * self.control) + self.auto_control(theta, dtheta_dt, mom_mass_1, mom_mass_2, g, dt)

class ProportionalControl:
    def __init__(self, constant):
        self.constant = constant
    def __call__(self, theta, dtheta_dt, mom_mass_1, mom_mass_2, g, dt):
        return -self.constant * theta

class SineNoise:
    def __init__(self, strength_fn, components):
        self.strength_fn = strength_fn
        self.frequency_components = [(2 * math.pi / period, amplitude) for (period, amplitude) in components]
    def __call__(self, t):
        noise = sum([amplitude * math.sin(frequency * t) for (frequency, amplitude) in self.frequency_components])
        return self.strength_fn(t) * noise


if __name__ == '__main__':
    control = ProportionalControl(10)
    simulation = Simulation(SineNoise(
        lambda t: 0.5 + t / 20,
        [(0.73, 1), (2, 1), (2.9, 0.5), (13, 0.5)])
    )
    for i in range(0, 20000):
        simulation.step(control)
        if i % 1000 == 0:
            print(simulation.theta)
