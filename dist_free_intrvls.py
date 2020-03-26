import numpy as np
import scipy.stats as st
import scipy.optimize as opt

def one_side_upper_conf_bound(p, X, oneminalpha):
    """ Calculate an interpolated upper confidence bound for the quantile p in sample X
        with upper confidence bound oneminalpha as per page 81 in 'Statistical Intervals A Guide 
        for Practitioners and Researchers' by William Q. Meeker, Gerald J. Hahn, Luis A. Escobar
    """
    
    # sort samples
    X = np.sort(X)

    # count number of samples
    n = len(X)

    u_c = np.int(st.binom.ppf(oneminalpha, n, p)+1)
    # now need to find the next order statistic < X[u_c-1]
    # concat [0] means that we pick the first entry if there is no value of X < X[u_c-1]
    u_n = np.concatenate([[0],np.arange(1,len(X)+1)[X<X[u_c-1]]])[-1]
    
    #print('X[u_c] = {}, X[u_n] = {}'.format(X[u_c], X[u_n]))
    if X[u_c-1] == X[u_n-1]:
        print('Upper conf bound interpolation not possible')
        omega = 1
    else:
        omega = (oneminalpha - st.binom.cdf(u_n-1, n, p))/(st.binom.cdf(u_c-1, n, p) - st.binom.cdf(u_n-1, n, p))
    
    return omega*X[u_c-1] + (1 - omega)*X[u_n-1]

def one_side_lower_conf_bound(p, X, oneminalpha):
    """ Calculate an interpolated lower confidence bound for the quantile p in sample X
        with lower confidence bound oneminalpha as per page 82 in 'Statistical Intervals A Guide 
        for Practitioners and Researchers' by William Q. Meeker, Gerald J. Hahn, Luis A. Escobar
    """
    
    # sort samples
    X = np.sort(X)

    # count number of samples
    n = len(X)

    l_c = n - np.int(st.binom.ppf(oneminalpha, n, 1-p))
    # now need to find the next order statistic > X[l_c-1]
    # concat [len(X)-1] means that we pick the last entry if there is no value of X > X[l_c]
    l_n = np.concatenate([np.arange(1,len(X)+1)[X>X[l_c-1]],[len(X)-1]])[0]

    #print('X[l_c] = {}, X[l_n] = {}'.format(X[l_c], X[l_n]))
    if X[l_c-1] == X[l_n-1]:
        print('Lower conf bound interpolation not possible')
        omega = 1
    else:
        omega = (oneminalpha - (1-st.binom.cdf(l_n-1, n, p)))/((1-st.binom.cdf(l_c-1, n, p)) - (1-st.binom.cdf(l_n-1, n, p)))
    
    return omega*X[l_c-1] + (1 - omega)*X[l_n-1]

def two_sided_conf_bound(p, X, oneminalpha):
    """ Calculate an interpolated two-sided confidence bound for the quantile p in sample X
        with confidence interval oneminalpha as per page 82 in 'Statistical Intervals A Guide 
        for Practitioners and Researchers' by William Q. Meeker, Gerald J. Hahn, Luis A. Escobar
    """
    
    # calculate 100(1 − α/2)% upper conf bound
    upper_bound = one_side_upper_conf_bound(p, X, 1-(1-oneminalpha)/2)
    
    # calculate 100(1 + α/2)% lower conf bound
    lower_bound = one_side_lower_conf_bound(p, X, 1-(1-oneminalpha)/2)
    
    return [lower_bound, upper_bound]

def two_sided_tol_intrvls(beta, X, oneminalpha):
    """ Calculate tolerance intervals for containing a fraction of the population
        beta given sample X from that population, with confidence oneminalpha as 
        per page 86 in 'Statistical Intervals A Guide for Practitioners and 
        Researchers' by William Q. Meeker, Gerald J. Hahn, Luis A. Escobar
    """
    
    # sort samples
    X = np.sort(X)

    # count number of samples
    n = len(X)
    
    nu = n - np.int(st.binom.ppf(oneminalpha, n, beta))
    
    if nu < 2:
        print("""No two-sided distribution-free tolerance interval containing 
at least a proportion β with coverage probability greater than 
or equal to 1 − α possible.""")
        return [0,0]
    
    if nu%2:
        # nu is odd
        nu_1 = nu/2 - 0.5
        nu_2 = nu_1 + 1
    else:
        # nu is even
        nu_1 = nu/2
        nu_2 = nu/2
    
    nu_1 = int(nu_1)
    nu_2 = int(nu_2)
    
    l = nu_1
    u = n - nu_2 +1
    
    print('Confidence bound = {:.3f} (desired = {})'.format(st.binom.cdf(u-l-1, n, beta),oneminalpha))
    tol_bounds = [X[l-1], X[u-1]]
    
    return tol_bounds

def two_sided_interp_tol_intrvls(beta, X, oneminalpha):
    """ Calculate interpolated tolerance intervals for containing a fraction of the population
        beta given sample X from that population, with confidence oneminalpha as 
        per page 87 in 'Statistical Intervals A Guide for Practitioners and 
        Researchers' by William Q. Meeker, Gerald J. Hahn, Luis A. Escobar
    """
    
    # sort samples
    X = np.sort(X)

    # count number of samples
    n = len(X)
    
    nu = n - np.int(st.binom.ppf(oneminalpha, n, beta))
    
    if nu < 2:
        print("""No two-sided distribution-free tolerance interval containing 
at least a proportion β with coverage probability greater than 
or equal to 1 − α possible.""")
        return [0,0]
    
    if nu%2:
        # nu is odd
        nu = nu -1
        
    l_c = int(nu/2)
    l_n = l_c + 1
    u_c = int(n - l_c + 1)
    u_n = int(n - l_n + 1)
    
    omega = (oneminalpha - st.binom.cdf(u_n-l_n-1, n, beta))/(st.binom.cdf(u_c-l_c-1, n, beta) - st.binom.cdf(u_n-l_n-1, n, beta))
    
    tol_bounds = [omega*X[l_c-1] + (1-omega)*X[l_n-1], omega*X[u_c-1] + (1-omega)*X[u_n-1]]
    
    return tol_bounds

def cond_on_n(n, beta, oneminalpha):
    """ Condition to be minimized for smallest n required for meaningful TI
        to be calculated, from page 89 in 'Statistical Intervals A Guide for Practitioners and 
        Researchers' by William Q. Meeker, Gerald J. Hahn, Luis A. Escobar
    """
    
    return (oneminalpha - (1-n*beta**(n-1) + (n-1)*beta**n))**2

def calc_min_n(beta, oneminalpha):
    """ Calculate the smallest n required to give meaningful interval for given beta and one minus alpha
    """
    
    res = opt.minimize_scalar(cond_on_n, args = (beta, oneminalpha))
    
    return np.ceil(res.x)