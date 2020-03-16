import numpy as np


def wheeler_z0(w: float, t: float, er: float, h: float) -> float:
    """
    Calculate the microstrip characteristic impedance for a given
    width using Wheeler's equation.  Wheeler's equation can be found
    at:

    https://en.wikipedia.org/wiki/Microstrip#Characteristic_impedance

    :param w: microstrip trace width (m)
    :param t: trace thickness (m)
    :param er: substrate relative permittivity
    :param h: substrate height (thickness) (m)

    :returns: characteristic impedance
    """
    z0 = 376.730313668
    weff = w + (
        (t * ((1 + (1 / er)) / (2 * np.pi)))
        * np.log(
            (4 * np.e)
            / (
                np.sqrt(
                    ((t / h) ** 2)
                    + (((1 / np.pi) * ((1 / ((w / t) + (11 / 10))))) ** 2)
                )
            )
        )
    )
    tmp1 = 4 * h / weff
    tmp2 = (14 + (8 / er)) / 11
    zm = (z0 / (2 * np.pi * np.sqrt(2 * (1 + er)))) * np.log(
        1
        + (
            tmp1
            * (
                (tmp2 * tmp1)
                + (
                    np.sqrt(
                        (
                            (tmp2 * tmp1) ** 2
                            + ((np.pi ** 2) * ((1 + (1 / er)) / 2))
                        )
                    )
                )
            )
        )
    )
    return zm


def wheeler_z0_width(
    z0: float,
    t: float,
    er: float,
    h: float,
    tol: float = 0.01,
    guess: float = 0.3,
) -> float:
    """
    Calculate the microstrip width for a given characteristic
    impedance using Wheeler's formula.

    :param z0: characteristic impedance (ohm)
    :param t: trace thickness (m)
    :param er: substrate relative permittivity
    :param h: substrate height (thickness) (m)
    :param tol: acceptable impedance tolerance (ohm)
    :param guess: an initial guess for the width (m).  This can
        improve convergence time when the approximate width is known.

    :returns: trace width (m)
    """
    width = guess
    zm = wheeler_z0(w=width, t=t, er=er, h=h)
    wlow = width / 10
    zlow = wheeler_z0(w=wlow, t=t, er=er, h=h)
    # inverse relation between width and z0
    while zlow < z0:
        wlow /= 10
        zlow = wheeler_z0(w=wlow, t=t, er=er, h=h)

    whigh = width * 10
    zhigh = wheeler_z0(w=whigh, t=t, er=er, h=h)
    while zhigh > z0:
        whigh *= 10
        zhigh = wheeler_z0(w=whigh, t=t, er=er, h=h)

    while np.absolute(zm - z0) > tol:
        if zm > z0:
            m = (zhigh - zm) / (whigh - width)
            wlow = width
            zlow = zm
        else:
            m = (zm - zlow) / (width - wlow)
            whigh = width
            zhigh = zm

        # use linear interpolation to update guess
        width = width + ((z0 - zm) / m)
        zm = wheeler_z0(w=width, t=t, er=er, h=h)

    return width


def miter(trace_width: float, substrate_height: float) -> float:
    """
    Compute the optimal miter length using the Douville and James
    equation.
    """
    if trace_width / substrate_height < 0.25:
        raise ValueError(
            "Ratio of trace width to height must be at least 0.25."
        )
    return 0.52 + (0.65 * np.exp(-(27 / 20) * trace_width / substrate_height))


def coax_core_diameter(
    outer_diameter: float, permittivity: float, impedance: float = 50
) -> float:
    """
    Approximate coaxial cable core diameter for a given target
    characteristic impedance and outer diameter.

    :returns: Inner core diameter.  The units will match those of the
              provided outer diameter.
    """
    return outer_diameter / np.power(
        10, impedance * np.sqrt(permittivity) / 138
    )
