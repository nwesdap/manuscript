import numpy as np


def std_Sn(a):
    # https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/diffsn.htm
    #
    # Peter J. Rousseuw and Christophe Croux (1993), "Alternatives to the Median
    # Absolute Deviation," Journal of the American Statistical Association, Vol. 88,
    # No. 424, pp. 1273-1283.
    a = a[~np.isnan(a)].ravel()
    sn0 = np.full((np.size(a), np.size(a)), np.nan)
    for i in range(len(a)):
        sn0[i] = np.abs(a[i] - a)
    np.fill_diagonal(sn0, np.nan)
    sn1 = np.nanmedian(sn0, axis=1)
    sn = 1.1926 * np.median(sn1)
    return sn
