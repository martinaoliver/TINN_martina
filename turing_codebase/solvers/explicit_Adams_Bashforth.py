import numpy as np
import numba
from numba import cuda, float32


@numba.jit(nopython=True)
def integrate(c0, t, dt, n, L, Ds, f, f_args):
    t_c = t[0]
    c_c = c0.copy()
    dc_1 = np.zeros_like(c_c)
    dc_2 = None
    d_ret = np.zeros((c0.shape[0], c0.shape[1], c0.shape[2], t.shape[0]))
    d_ret[:, :, :, 0] = c_c.copy()
    c_num = c0.shape[0]
    for t_i, t_next in enumerate(t[1:]):
        while t_c < t_next:
            f_f = f(c_c, t_c, f_args)
            for i in range(n[0]):
                for j in range(n[1]):
                    # Periodic boundary condition
                    i_prev = (i - 1) % n[0]
                    i_next = (i + 1) % n[0]

                    j_prev = (j - 1) % n[1]
                    j_next = (j + 1) % n[1]
                    for k in range(c_num):
                        dc_1[k, i, j] = (Ds[k] * n[k] / L[k]) * (
                            c_c[k, i_prev, j]
                            + c_c[k, i_next, j]
                            + c_c[k, i, j_prev]
                            + c_c[k, i, j_next]
                            - 4.0 * c_c[k, i, j]
                        ) + f_f[k, i, j]

            # c_c += dt * dc
            if dc_2 is None:
                dc_2 = dc_1.copy()
            c_c += dt * (1.5 * dc_1 - 0.5 * dc_2)
            t_c += dt
            # store dc_1 in dc_2 for the next iteration
            dc_2 = dc_1.copy()
        d_ret[:, :, :, t_i + 1] = c_c.copy()
    return d_ret
