![Logo](resource/LOGO.png)

# Kate 2.0
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/kaiCbs/StockOpt/blob/master/README.md)


## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Multi-Factor Strategy Design](#multi-factor-strategy-design)
- [Maintainers](#maintainers)
- [License](#license)

## Background

Kate (short for Kai alpha testing engine) is a extreme light Python algorithmic backtesting framework supporting multiple securities. There are already many similar and excellent backtesting packages and platform using Python. Like RiceQuant' rqalpha, Quantopian' zipline etc. 

Kate's advantage is that it's extremely easy to use and require almost zero learning cost. However, there is always trade-off, that means it might not be very flexible compares to other platforms (though you can always find your way to hack :P)


## Install

Download the source code from github:

    $ git clone git@github.com:kaiCbs/Kate.git


## Usage

An alpha is considered one of good quality when: 

> - The idea and expression is simple.  
> - The expression/code is elegant.  
> - It has good in‐sample Sharpe.  
> - It is not sensitive to small changes in data and parameters.   
> - It works in multiple universes.
> - It works in different regions.
> - Its profit hits a recent new high. 


Here a snippet of a simple alpha strategy based on [101 Formulaic](https://arxiv.org/ftp/arxiv/papers/1601/1601.00991.pdf) Alpha#42: `(rank((vwap - close)) / rank((vwap + close)))`


```
from Kate.Intraday.AlphaBase import *

class Alpha(Intraday): 

    def __init__(self, sim_start, sim_end, **kwargs):
        super().__init__(sim_start, sim_end, **kwargs)
        
    def alpha(self):
        vwap = (self.price * self.volume).sum() / self.volume.sum()
        twap = self.price.mean()
        close = self.price.iloc[-5:,:].mean()
        factor = (vwap - close) / (vwap + close)
        return factor
        

if __name__ == "__main__":
    agent = Alpha("2010-01-05", "2020-05-08")
    agent.run()
```

Basically, all you need to do is filling the alpha formula part. Then it will give you the result on the fly.

```
(base) kai@f9f874b32b8e:~/project$ python alphaPools/alpha20.py 

Welcome to Kate version 2.0.1 (2020-05-25)

 * Documentation:   https://github.com/kaiCbs/Kate
 * Support:         kx2153@gsb.columbia.edu

Copyright (C) 2020 Kai Xiang

[0:00:01.337949] 2010-01-29 excess return:  1.007      cumulative return:  1.007      winning rate:  0.473
[0:00:02.362246] 2010-02-26 excess return:  1.015      cumulative return:  1.023      winning rate:  0.733
[0:00:03.903434] 2010-03-31 excess return:  1.026      cumulative return:  1.050      winning rate:  0.782
[0:00:05.296545] 2010-04-30 excess return:  1.037      cumulative return:  1.089      winning rate:  0.666
[0:00:06.633856] 2010-05-31 excess return:  1.035      cumulative return:  1.128      winning rate:  0.750
[0:00:07.990946] 2010-06-30 excess return:  1.011      cumulative return:  1.141      winning rate:  0.736
[0:00:09.626907] 2010-07-30 excess return:  1.019      cumulative return:  1.163      winning rate:  0.818
[0:00:11.210271] 2010-08-31 excess return:  1.014      cumulative return:  1.179      winning rate:  0.599
[0:00:12.604921] 2010-09-30 excess return:  1.014      cumulative return:  1.197      winning rate:  0.526
[0:00:13.762312] 2010-10-29 excess return:  1.051      cumulative return:  1.259      winning rate:  0.750
[0:00:15.357200] 2010-11-30 excess return:  1.017      cumulative return:  1.280      winning rate:  0.636
[0:00:17.050345] 2010-12-31 excess return:  1.032      cumulative return:  1.322      winning rate:  0.826
[0:00:18.620371] 2011-01-31 excess return:  1.029      cumulative return:  1.362      winning rate:  0.650
......

```
After the simulation, it will also report annual performance and correlation with existing alphas in the pool.
```
         Sharpe       long     short  bp(hedged)     return        ir
year                                                                
2010  6.650449   0.532726  0.098524   14.007728   0.397406  0.418939
2011  5.598640  -0.134870 -0.303090    9.086694   0.247086  0.352681
2012  5.587949   0.241947 -0.002807    9.260765   0.251190  0.352008
2013  8.490396   0.796634  0.203825   17.060392   0.498537  0.534845
2014  8.354060   1.122841  0.398076   17.264187   0.523938  0.526256
2015  6.900240   2.459565  0.844824   26.157824   0.883343  0.434674
2016  6.846995   0.262960 -0.125724   15.554995   0.458890  0.431320
2017  2.989286  -0.041204 -0.191324    7.346871   0.194046  0.188307
2018  5.150990  -0.132711 -0.331611   11.102729   0.307653  0.324482
2019  1.532943   0.262348  0.188202    2.744121   0.068192  0.096566
2020  1.288325   0.084480  0.057552    3.714698   0.029678  0.081157
Avg.  5.445524  30.241224  0.407535   12.652772  22.495975  0.343036 

            corr       bp      ir
alpha020  1.0000  12.7025  0.3436
alpha021  0.8433  10.1180  0.3411
alpha008  0.8344  10.2070  0.2798
alpha022  0.8047  10.3213  0.3365
alpha007  0.6721   6.3747  0.1680
......
alpha006 -0.0429   7.6620  0.2220
alpha004 -0.1125   4.3175  0.1109
alpha010 -0.1334   2.3005  0.1334
alpha005 -0.2202   5.9003  0.1488
alpha011 -0.3444   1.9009  0.0368
```

Also, you can get a pnl curve and the drawdown during this period.
![pnl curve](/resource/simResult.png)


## Multi-Factor Strategy Design

### Alpha factor correlation analysis

In order to reduce the risk exposure and take full advantage of the premium against the market from evert single factor, but first of all, we want to the correlation among our factors as low as possible, so each of them might have a relatively high "marginal" contribution.

The poolCorr.py will generate a correlation matrix, that tells the correlation among our alpha factors.

![corr matrix](/resource/corrmat.png)


### Dynamic allocated weights

We can assign a dynamic weight to all our factor values, ideally it will have better properties compares to any single factor in the terms of maximum drawdown, sharpe, return etc.


```
(base)  kai@f9f874b32b8e:~/project$ python ./utils/portfolio.py

Welcome to Kate version 2.0.1 (2020-05-25)

 * Documentation:   https://github.com/kaiCbs/Kate
 * Support:         kx2153@gsb.columbia.edu

Copyright (C) 2020 Kai Xiang


[0:00:12.941444] 2015-01-30 excess return:  1.0348      cumulative return:  1.0348      winning rate:  0.7000
[0:00:22.698075] 2015-02-27 excess return:  1.0285      cumulative return:  1.0644      winning rate:  0.8000
[0:00:36.994951] 2015-03-31 excess return:  1.0949      cumulative return:  1.1654      winning rate:  0.9091
[0:00:50.536079] 2015-04-30 excess return:  1.0705      cumulative return:  1.2475      winning rate:  0.7619
[0:01:03.626321] 2015-05-29 excess return:  1.0876      cumulative return:  1.3568      winning rate:  0.7000
[0:01:17.505793] 2015-06-30 excess return:  1.0785      cumulative return:  1.4633      winning rate:  0.7619
[0:01:31.310690] 2015-07-31 excess return:  0.9715      cumulative return:  1.4216      winning rate:  0.4783
[0:01:44.721175] 2015-08-31 excess return:  1.0837      cumulative return:  1.5406      winning rate:  0.7143
[0:01:57.571873] 2015-09-30 excess return:  1.0834      cumulative return:  1.6692      winning rate:  0.8000
[0:02:08.698180] 2015-10-30 excess return:  1.0556      cumulative return:  1.7620      winning rate:  0.8235
......



         Sharpe      long     short  bp(hedged)    return        ir
year                                                              
2015  9.005327  2.691887  0.818824   29.349237  1.031793  0.567282
2016  6.967989  0.136113 -0.125724   10.799757  0.300355  0.438942
2017  3.832732 -0.064929 -0.191324    6.001086  0.156770  0.241439
2018  5.829338 -0.157835 -0.331611    9.624070  0.262283  0.367214
2019  5.593034  0.387889  0.188202    6.323506  0.166321  0.352328
2020  2.337344  0.103369  0.057552    5.391913  0.044072  0.147239
Avg.  5.803072  4.058093  0.080029   11.970439  3.697791  0.365559 

            corr       bp      ir
alpha032  0.6334   4.1913  0.1544
alpha018  0.6281   6.7516  0.2031
alpha003  0.6106   3.6539  0.1476
alpha021  0.6058   9.9615  0.3041
alpha022  0.5562  10.1820  0.2971
alpha007  0.5478   5.6491  0.1354
......
alpha023  0.1710   6.8478  0.1923
alpha011  0.1601   3.0224  0.0525
alpha010  0.0879   2.8764  0.1443
alpha026  0.0569   0.8369  0.0364
alpha014  0.0210   2.9426  0.0794
alpha027  0.0096   2.5283  0.1005
```

![sim pnl](/resource/multifactor.png)

## Maintainers

[@kaiCbs](https://github.com/kaiCbs).


## License

[GNU General Public License](resource/GNU.txt)