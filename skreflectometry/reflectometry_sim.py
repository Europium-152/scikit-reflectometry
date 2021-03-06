from __future__ import print_function, division, absolute_import
from builtins import range
import numpy as np
from scipy.integrate import simps
from scipy.constants import speed_of_light
from scipy.signal import spectrogram


def phase_delay(freq_probing, radius_arr, refractive_mat, refract_epsilon=1e-6,
                antenna_side='hfs', reflect_at_wall=True, method='trapz'):
    """
    TODO
    Parameters
    ----------
    freq_probing
    radius_arr
    refractive_mat
    refract_epsilon
    antenna_side
    reflect_at_wall : bool
        TODO
    method : str {'trapz', 'simps'}, optional

    Returns
    -------

    Raises
    ------
    ValueError
        If the `method` selected does not exist.
    """

    if antenna_side == 'lfs':
        refractive_mat = refractive_mat[:, ::-1]

    # Returns the index of the first position where refraction < epsilon for
    #   every sampling frequency. If there is no such point, it returns 0.
    reflect_pos_ind = np.argmax(refractive_mat <= refract_epsilon, axis=1)

    # Find if reflect_pos_ind == 0 are real reflections at entrance (pos = 0)
    #   or no reflection in the plasma.
    reflect_at_0_ind = (refractive_mat[:, 0] <= refract_epsilon)
    reflect_at_0_measured_ind = (reflect_pos_ind == 0)
    reflect_at_0_fake_ind = reflect_at_0_ind ^ reflect_at_0_measured_ind

    if reflect_at_wall:  # TODO
        reflect_pos_ind[reflect_at_0_fake_ind] = - 1
    else:
        reflect_pos_ind[reflect_at_0_fake_ind] = 0

    if method == 'trapz':
        integral_func = np.trapz
    elif method == 'simps':
        integral_func = simps
    else:
        raise ValueError("Parameter 'method' must be 'trapz' or 'simps'")

    refract_mat_temp = np.copy(refractive_mat)
    for freq_ind in range(len(freq_probing)):
        refract_mat_temp[freq_ind, reflect_pos_ind[freq_ind]:-1] = 0

    refract_int = integral_func(refract_mat_temp, radius_arr, axis=1)

    phase_diff = 2 * 2 * np.pi * freq_probing / speed_of_light * refract_int
    phase_diff -= np.pi / 2

    return phase_diff


def group_delay(freq_probing, phase_delay_arr):
    """
    TODO
    Parameters
    ----------
    freq_probing
    phase_delay_arr

    Returns
    -------

    """

    phase_diff = np.gradient(phase_delay_arr)
    omega_diff = np.gradient(2 * np.pi * freq_probing)

    return phase_diff / omega_diff


# def beat_spectrogram(beat, fs=1.0,
#                      nperseg=136, nfft=2048, noverlap=128):
#     """
#     TODO
#     Parameters
#     ----------
#     freq_samp
#     time_delay_arr
#     fs
#     nperseg
#     nfft
#     noverlap
#
#     Returns
#     -------
#
#     """
#
#     freqs, times, spectrum = \
#         spectrogram(beat, fs=fs,
#                     nperseg=nperseg, nfft=nfft, noverlap=noverlap)
#
#     return freqs, times, spectrum


def beat_signal(freq_probing, time_delay_arr):
    """
    TODO
    Parameters
    ----------
    freq_probing
    time_delay_arr

    Returns
    -------

    """

    return np.cos(np.cumsum(time_delay_arr * np.gradient(2 * np.pi * freq_probing)))


def beat_maximums(freqs, spectrum):
    """
    TODO
    Parameters
    ----------
    freqs
    spectrum

    Returns
    -------

    """

    return freqs[np.argmax(spectrum, axis=0)]
