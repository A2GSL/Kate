Kate (short for Kai alpha trading engine) is a extreme light Python algorithmic backtesting framework supporting multiple securities. There are already many similar and excellent backtesting packages and platform using Python. Like RiceQuant' rqalpha, Quantopian' zipline etc. 

Kate's advantage is that it's extremely easy to use and require almost zero learning cost. However, there is always trade-off, that means it might not be very flexible compares to other platforms (though you can always find your way to hack :P)


## Develop an Alpha

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
from KatePublic.Intraday.AlphaBase import *

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
(/home/highfort/.conda/KaiWork) highfort@f9f874b32b8e:~/project$ python alphaPools/alpha20.py 
[0:00:01.337949] 2010-01-29 excess return:  1.0076      cumulative return:  1.0076      winning rate:  0.4737
[0:00:02.362246] 2010-02-26 excess return:  1.0156      cumulative return:  1.0233      winning rate:  0.7333
[0:00:03.903434] 2010-03-31 excess return:  1.0263      cumulative return:  1.0502      winning rate:  0.7826
[0:00:05.296545] 2010-04-30 excess return:  1.0374      cumulative return:  1.0895      winning rate:  0.6667
[0:00:06.633856] 2010-05-31 excess return:  1.0357      cumulative return:  1.1284      winning rate:  0.7500
[0:00:07.990946] 2010-06-30 excess return:  1.0114      cumulative return:  1.1413      winning rate:  0.7368
[0:00:09.626907] 2010-07-30 excess return:  1.0195      cumulative return:  1.1636      winning rate:  0.8182
[0:00:11.210271] 2010-08-31 excess return:  1.0140      cumulative return:  1.1799      winning rate:  0.5909
[0:00:12.604921] 2010-09-30 excess return:  1.0148      cumulative return:  1.1974      winning rate:  0.5263
[0:00:13.762312] 2010-10-29 excess return:  1.0515      cumulative return:  1.2590      winning rate:  0.7500
[0:00:15.357200] 2010-11-30 excess return:  1.0171      cumulative return:  1.2806      winning rate:  0.6364
[0:00:17.050345] 2010-12-31 excess return:  1.0329      cumulative return:  1.3228      winning rate:  0.8261
[0:00:18.620371] 2011-01-31 excess return:  1.0297      cumulative return:  1.3620      winning rate:  0.6500
[0:00:19.773529] 2011-02-28 excess return:  1.0298      cumulative return:  1.4026      winning rate:  0.7333
[0:00:21.526875] 2011-03-31 excess return:  1.0169      cumulative return:  1.4262      winning rate:  0.6957
[0:00:22.927034] 2011-04-29 excess return:  1.0212      cumulative return:  1.4564      winning rate:  0.7368
[0:00:24.473499] 2011-05-31 excess return:  1.0065      cumulative return:  1.4658      winning rate:  0.5714
[0:00:26.060568] 2011-06-30 excess return:  1.0237      cumulative return:  1.5006      winning rate:  0.7143
[0:00:27.703943] 2011-07-29 excess return:  1.0150      cumulative return:  1.5231      winning rate:  0.6667
[0:00:29.601038] 2011-08-31 excess return:  1.0261      cumulative return:  1.5629      winning rate:  0.6087
[0:00:31.257441] 2011-09-30 excess return:  0.9894      cumulative return:  1.5463      winning rate:  0.5238
[0:00:32.522283] 2011-10-31 excess return:  1.0119      cumulative return:  1.5647      winning rate:  0.6250
[0:00:34.258634] 2011-11-30 excess return:  1.0047      cumulative return:  1.5721      winning rate:  0.5909
[0:00:36.007063] 2011-12-30 excess return:  0.9779      cumulative return:  1.5374      winning rate:  0.3636
[0:00:37.207626] 2012-01-31 excess return:  1.0182      cumulative return:  1.5654      winning rate:  0.7333
[0:00:38.972407] 2012-02-29 excess return:  1.0215      cumulative return:  1.5990      winning rate:  0.7143
[0:00:40.725055] 2012-03-30 excess return:  1.0123      cumulative return:  1.6186      winning rate:  0.7273
[0:00:42.015164] 2012-04-27 excess return:  1.0268      cumulative return:  1.6619      winning rate:  0.7647
[0:00:43.768317] 2012-05-31 excess return:  1.0150      cumulative return:  1.6868      winning rate:  0.7273
[0:00:45.383637] 2012-06-29 excess return:  0.9966      cumulative return:  1.6811      winning rate:  0.5000
[0:00:47.270313] 2012-07-31 excess return:  0.9971      cumulative return:  1.6762      winning rate:  0.5455
[0:00:49.174987] 2012-08-31 excess return:  1.0265      cumulative return:  1.7206      winning rate:  0.6522
[0:00:50.854428] 2012-09-28 excess return:  1.0128      cumulative return:  1.7426      winning rate:  0.6500
[0:00:52.406748] 2012-10-31 excess return:  1.0280      cumulative return:  1.7913      winning rate:  0.8889
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
alpha012  0.6580   3.7781  0.0852
alpha018  0.6046   8.4897  0.2755
alpha013  0.5583   3.0672  0.0732
alpha019  0.5340   8.6347  0.3114
alpha015  0.4983   4.0230  0.1469
alpha003  0.4650   5.1257  0.2063
alpha014  0.4535   6.7338  0.2075
alpha001  0.3744   4.6399  0.1763
alpha035  0.3288   4.4780  0.1499
alpha034  0.3040   2.3663  0.0747
alpha002  0.2852   3.2414  0.1070
alpha032  0.2518   4.0779  0.1550
alpha031  0.2278   7.6725  0.2589
alpha009  0.2245   5.7338  0.1625
alpha017  0.1985   3.5664  0.1786
alpha030  0.1648   4.4840  0.2115
alpha029  0.1644   4.5273  0.2243
alpha016  0.1637   3.3101  0.1650
alpha026  0.1485   2.0419  0.1004
alpha033  0.1323   4.5522  0.2396
alpha024  0.1037   5.3915  0.1656
alpha028  0.0935   4.4148  0.2040
alpha027  0.0323   2.2613  0.1050
alpha025  0.0193   4.1051  0.1218
alpha023 -0.0013   5.6101  0.1714
alpha006 -0.0429   7.6620  0.2220
alpha004 -0.1125   4.3175  0.1109
alpha010 -0.1334   2.3005  0.1334
alpha005 -0.2202   5.9003  0.1488
alpha011 -0.3444   1.9009  0.0368
```

Also, you can get a pnl curve and the drawdown during this period, as we can see, this alpha factor works pretty good in the past, but relatively weak in recent two years, that is because Chinese A-share market style has changed a lot after 2018.
![pnl curve](/resource/sim.png)

## Portfolio Analysis

```
corr = pd.read_csv("poolCorr.csv", index_col=0)
corr = corr.sort_values("alpha008", ascending=False)
corr = corr[corr.index]
corr.style.background_gradient(cmap='coolwarm').set_precision(3)
```

We poolCorr.py will generate a correlation matrix, that tells the correlation among your alpha factors.
![corr matrix](/resource/corrmat.png)


To be continued