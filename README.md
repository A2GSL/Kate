Kate is a extreme light Python algorithmic backtesting framework supporting multiple securities. There are already many similar and excellent backtesting packages and platform using Python. Like RiceQuant' rqalpha, Quantopian' zipline etc. 

Kate's advantage is that it's extremely easy to use and require almost zero learning cost. However, there is always trade-off, that means it might not be very flexible compares to other platforms (though you can always find your way to hack :P)

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
(/home/highfort/.conda/KaiWork) highfort@f9f874b32b8e:~/project$ python alphaPools/alpha8.py 
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
```
