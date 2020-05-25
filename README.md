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

