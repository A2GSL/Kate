from db_tools import *
import matplotlib.pyplot as plt

class Interday:
    
    def __init__(self, sim_start, sim_end):
        """
        Initialize the strategy, simulate day by day in a rolling manner
        """
        self.sim_start = sim_start
        self.sim_end = sim_end
        self.queue = CALENDAR[CALENDAR.index(self.sim_start):CALENDAR.index(self.sim_end)+1][::-1]
        #self.history = []
        self.cum_return = 1
        self.commission = 0
        self.walked = 0
        self.weights = None
        self.pool = None
        self.nextTradingDate =  self.sim_start
 

    def update(self):
        self.lastpool = self.pool
        self.now = self.queue.pop()
        self._price = fetch(self.now, field="price")
        self._volume = fetch(self.now, field="volume")
        tradingStatus = fetch(self.now, field="tradingstatus")
        self.tradingStatusRaw = tradingStatus if len(tradingStatus) else self.tradingStatusRaw
            
        
        self.pool = [stock for stock in self._volume if stock in self.tradingStatusRaw]
        
        self.tradingStatus = (self.tradingStatusRaw[self.pool] == 'trade').values[0]
            
        self.price = self._price[self.pool].iloc[:,self.tradingStatus]   # keep those tradable
        self.volume = self._volume[self.pool].iloc[:,self.tradingStatus]   
        self.close = self.price.iloc[-1,:]
        
        self.pool = self.price.columns
        self.numStocks = len(self.pool)
        self.nextTradingDate = self.queue[-1] if self.queue else None
        if self.nextTradingDate:
            self.nextClose = fetch(self.nextTradingDate, field="close")[self.pool]
            self.nextReturn = (self.nextClose-self.close)/self.close 
        self.signal = self.alpha().fillna(0)
        self.lastWeights = self.weights
        self.weights = self.allocate()
        self.turnover = self._turnover()

        
    def _turnover(self):
        if not self.lastWeights:
            return 0
        
        common = [s for s in self.lastpool if s in self.pool]
        long_turnover = np.minimum(pd.DataFrame([self.lastWeights["long"]], columns=self.lastpool)[common],
                   pd.DataFrame([self.weights["long"]], columns=self.pool)[common]).sum(axis=1).values / self.lastWeights["long"].sum()
        short_turnover = np.minimum(pd.DataFrame([self.lastWeights["short"]], columns=self.lastpool)[common],
                   pd.DataFrame([self.weights["short"]], columns=self.pool)[common]).sum(axis=1).values / self.lastWeights["short"].sum()
        
        return (1 - (long_turnover + short_turnover)/2)[0]
        
    def alpha(self):
        """
        (Should be rewrite) A Demonstrative example that using intraday volatility as indicator 
        Fields avaiable:
         - self.price
         - self.volume
        """
        return self.price.std() / self.price.mean()

    
    def allocate(self):
        """
        (Should be rewrite) This function assgins different weights of AUM on stocks, default equally allocate on top 20% and buttom 20% stocks (long/short)  
        """
        
        long_stock = (self.signal < np.quantile(self.signal, 0.2)).values
        # print(long_stock.sum(), long_stock.shape,  np.quantile(self.signal, 0.2), self.signal.isnull().sum())
        short_stock = np.ones_like(long_stock)  # fake index
        return {"long":long_stock.astype(int), "short": short_stock.astype(int)}
    

    def run(self, log = True, verbose = True):
        """
        Evaluate of strategy performance, in terms of portfolio return and prediction-reality correlation
        """
        startTime = datetime.datetime.now()
        self.log_time = str(datetime.datetime.now())
        with open("./logs/log-{}.csv".format(self.log_time), "w") as output:
            print("date,long,short,excess return,culmulative return,turnover", file=output)
            while len(self.queue)>1:
                self.update()
                long_part = (self.weights["long"] * self.nextReturn).sum() / self.weights["long"].sum()
                short_part = (self.weights["short"] * self.nextReturn).sum() / self.weights["short"].sum()
                excess_return =  long_part - short_part
                self.cum_return *= (1+excess_return)
                if log: print(self.now, long_part, short_part, excess_return, self.cum_return, self.turnover,sep=",", file=output)
                if verbose: print("[{}]".format(datetime.datetime.now() - startTime), self.now, 
                                  "  \tlong: {:7.4f}  \tshort: {:7.4f}  \texcess return: {:7.4f}  \tcumulative return: {:7.4f}  \tturnover: {:7.4f}".format(
                                    long_part, short_part, excess_return, self.cum_return, self.turnover))    
        Intraday.evaluate(self.log_time)
    
    @classmethod
    def evaluate(cls, log_time):
        result = pd.read_csv("./logs/log-{}.csv".format(log_time))
        result["date"] = result["date"].astype(np.datetime64)
        result["historyHigh"] = [max(result["culmulative return"][:i+1]) for i in range(len(result))]
        result["drawdown"] = result["historyHigh"]/result["culmulative return"]-1
        fig, ax = plt.subplots(figsize=(10,6))
        ax2 = ax.twinx()
        ax2.set(ylim=(0, max(result["drawdown"]) * 2.5))
        ax.plot(result["date"], (result["long"]+1).cumprod(), c = "red", label = "Long")
        ax.plot(result["date"], (result["short"]+1).cumprod(), c = "green", label = "Short(index)")
        ax.plot(result["date"], result["culmulative return"], c = "blue", label = "Hedged")
        ax.legend(bbox_to_anchor=(0.57, 0.95))
        #ax.plot(result["date"], (result["long"]-result["short"]+1).cumprod(), c = "green")

        fig.text(0.72, 0.3, '$Sharpe= {:.4f}$\n$Daily\ bp={:.4f}$'.format(
                np.sqrt(252) * result["excess return"].mean()/result["excess return"].std(),
                result["excess return"].mean() * 10000), fontsize=10)


        ax2.fill_between(result["date"], result["drawdown"], alpha=0.4)
        ax3 = fig.add_axes([.18, .65, .2, .2])
        ax3.hist(result["excess return"], bins=50, density=False, edgecolor="b", alpha=0.6)
        ax3.axvline(x=0, color = "red")
        fig.savefig('./graphs/{}.png'.format(log_time))
        fig.show()
