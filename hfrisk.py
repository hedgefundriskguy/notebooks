import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm

def get_drawdowns(timeseries):
    """
        Returns a time series of drawdowns for given time series
        Could be used to plot underwater curve
    """
    local_dd = lambda subts: subts[-1]/max(subts)-1
    cumret = (1+timeseries).cumprod()
    T = len(cumret)
    dds = np.zeros(T)

    for t in range(1, T):
        dds[t] = local_dd(cumret[0:t])

    dds[0] = cumret[0]/1 - 1
    return pd.Series(dds, index=timeseries.index)

def max_dd(timeseries):
    """
        Calculate Maximum drawdown from time series
    """
    dds = get_drawdowns(timeseries)
    return min(dds)

def calc_cumret(rets, i):
    """
        Calculate cumultaive return
    """
    col = rets.iloc[:,i]
    cumret = (1+col).cumprod()
    T = col.count()
    lastret = cumret.iloc[T-1]
    return lastret

def downside_deviation(rets, mar):
    """
     Calculate downside deviation
    """
    rets_dn = rets.copy()
    rets_dn[rets >= mar] = 0
    sum_sq = (rets_dn* rets_dn).sum()
    return np.sqrt(sum_sq / len(rets))

def basic_stats(rets):
    """
        Calculate basic hedge fund statistics
    """
    T = rets.count()[0]
    n_cols = len(rets. columns)
    means = np.mean(rets)
    sdevs = np.std(rets)
    annvol = sdevs * np.sqrt(12)
    vami = np.array([calc_cumret(rets, c) for c in range(n_cols)])
   
    annret = vami ** (12.0/T) - 1.0
    cumret = vami - 1
    mon_ret = vami[-1] ** (1.0/T) - 1.0;
    dds = [max_dd(rets.iloc[:,i]) for i in range(n_cols)]
    dn_dev = downside_deviation(rets,0) * np.sqrt(12)
    dict = { \
    'mu':means.values,  \
    'std':sdevs.values, \
     'cumret':cumret, \
     'annvol':annvol.values, \
     'annret':annret, \
     'sharpe':annret/annvol, \
     'vami':vami * 1000, \
     'var':means - 1.96 * sdevs, \
     'skew':stats.skew(rets), \
     'kurt':stats.kurtosis(rets), \
     'maxdd':dds, \
     'T':T,  \
     'dn_dev': dn_dev, \
     'sortino': mon_ret * 12 / dn_dev, \
     'mon_ret': mon_ret
      
     
     }
    return pd.DataFrame(dict)

def regime_analysis(rets):
    """
        Calculate fund performance in different market regimes
        Sample logic for figurong out regimes is defined in regimes notebook
    """
    group_by_regime = rets.groupby('Regime')
    ret_by_regime = group_by_regime.mean()
    return ret_by_regime


def factor_risk_attrib(fit, xdata, marketcols):
    """
        Calculate factor contribution to risk based on multi factor regression
        Based on Grinold and Kahn book
    """
    betas = fit.params
    betas_matrix = np.matrix(betas)
    betas_matrix_t = betas_matrix.T
    #factor covariance
    cov_matrix = np.matrix(xdata.cov())
    
    #total variance explained by factors
    tot_fact_var = betas_matrix * cov_matrix * betas_matrix_t

    res_var = np.std(fit.resid)**2

    #total variance is factor variance + variance of residuals
    totVar = tot_fact_var + res_var

    #factor marginal contribiution to risk
    fmctr = np.array(cov_matrix * betas_matrix_t)

    crisk = np.array(np.array(betas_matrix_t) * fmctr / totVar)

    tot_crisk = crisk.sum()
    criskmod = np.append(crisk, [1-tot_crisk])
    labels = np.append(marketcols, ['Unexplained'])


    return criskmod, labels
    
    

def read_data():
    """
        Reads data from market data csv file
    """
    marketdata = pd.DataFrame.from_csv('data/marketdata.csv')
    fund = marketdata['Fund']
    cols = marketdata.columns
    n_cols = len(cols)
    """ last column is regime. The other columns are returns """
    tsdata = marketdata[cols[0:n_cols-1]]
    factors = tsdata.iloc[:, 1:5]

    return fund, factors, tsdata
 

def convexity_analysis(tsdata, namex, namey):
    """
        perform convexity analysis of time series vs. specified factor
        convexity is evaluated using Treynor-Mazuy type formula:
            y = a + Bx + Bx^2
    """
    x = tsdata[namex]
    y = tsdata[namey]
    x2 = x**2
    tmydf = pd.DataFrame(data=[x, x2]).transpose()
    tmydf.columns = ['x', 'x2']
    model = sm.OLS(y, tmydf)
    modelfit = model.fit()
    betas = modelfit.params
    min_ret = x.min()
    max_ret = x.max()
    xfit = np.linspace(min_ret, max_ret, 100)
    yfit = betas[0]*xfit + betas[1]*(xfit**2)
    res = {'betas':betas, \
       'xhat':xfit, \
       'yhat':yfit, \
       'x':x, \
       'y':y}
    return res



