import math

# Write your controllers here

def none(theta, dtheta_dt, mom_mass_1, mom_mass_2, g, dt):
    return 0

def right(theta, dtheta_dt, mom_mass_1, mom_mass_2, g, dt):
    return 1

def left(theta, dtheta_dt, mom_mass_1, mom_mass_2, g, dt):
    return -1

def proportional_derivative(kp, kd):
    def control(theta, dtheta_dt, mom_mass_1, mom_mass_2, g, dt):
        return -kp * theta - kd * dtheta_dt
    return control

def energy(theta, dtheta_dt, mom_mass_1, mom_mass_2, g, dt):
    """Compute the (signed) impulse to return the pendulum to the top,
    using energy balance"""
    gpe = mom_mass_1 * g * (1 - math.cos(theta))
    target_momentum = math.copysign(mom_mass_2 * math.sqrt(2 * gpe / mom_mass_2), -theta)
    momentum = mom_mass_2 * dtheta_dt
    anti_gravity = -mom_mass_1 * g * math.sin(theta)
    return anti_gravity + (target_momentum - momentum) / dt

ALL = {
    'none': none,
    'right': right,
    'left': left,
    'pd-100-10': proportional_derivative(100, 10),
    'energy': energy
}
