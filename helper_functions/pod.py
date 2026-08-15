"""pod.py

qr_place adapted from https://github.com/Jan-Williams/pyshred/blob/main/processdata.py
"""
import numpy as np
import scipy


def svd_basis(data_matrix, num_sensors):
    """Compute POD basis, without QR

    Args:
        data_matrix (numpy array): training dataset of shape (N (number of training samples) x m (full-field size))
        num_sensors (int): number of sensors being used

    Returns:
        None
    """
    X_train = data_matrix.T  # invert to shape (m x N)
    U, S, Vt = np.linalg.svd(X_train, full_matrices=False)
    U_r = U[:, :num_sensors] # first num_sensors POD modes

    return U_r


def qr_place(data_matrix, num_sensors):
    """QR placement
    
    Takes a (N x m) data matrix consisting of N samples of an m dimensional state and 
    number of sensors, returns QR placed sensors and U_r for the SVD X = U S V^T

    Args:
        data_matrix (numpy array): training dataset
        num_sensors (int): number of sensors being used

    Returns:
        sensor_locs (): ...
        rankapprox (): ...
    """
    X_train = data_matrix.T  # invert to shape (m x N)
    u, s, v = np.linalg.svd(X_train, full_matrices=False)
    rankapprox = u[:, :num_sensors]
    q, r, pivot = scipy.linalg.qr(rankapprox.T, pivoting=True)
    sensor_locs = pivot[:num_sensors]

    return sensor_locs, rankapprox
