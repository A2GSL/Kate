import matplotlib.pyplot as plt
from collections import deque
from KATE.db_tools import *


class Intraday:
    def __init__(self, sim_start, sim_end, verbose=1, log=True):
        """
        Initialize the strategy, simulate day by day in a rolling manner
        """

        # the simulation periods
        self.sim_period = [d for d in CALENDAR
                           if sim_start <= d <= sim_end][::-1]

        # the real start and end date of the simulation
        self.sim_start = self.sim_period[-1]
        self.sim_end = self.sim_period[0]
        self.verbose = verbose
        self.log = log

        # initiate the state
        self.weights = None
        self.pool = None
        self.preSignal = None
        self.signal = None
        self.cum_return = 1
        self.nextTradingDate = self.sim_start
        self.description = None

        # configuration, strategy parameters
        self.historySize = 5
        self.positionSmooth = 10

        # history, previous price/volumns up to self.historySize, and previous alpha values
        self.recorderPrice = deque(maxlen=self.historySize)
        self.recorderVolume = deque(maxlen=self.historySize)
        self.history = deque(maxlen=self.historySize)

    def update(self):
        """
        function that assemble all components, update inner states, alphas, stock pool, return etc. 
        """

        self.now = self.sim_period.pop()
        self.priceRaw = fetch(self.now, field="price")
        self.volumeRaw = fetch(self.now, field="volume")
        tradingStatus = fetch(self.now, field="tradingstatus")
        self.tradingStatusRaw = tradingStatus if len(
            tradingStatus) else self.tradingStatusRaw
        self.tradingStatus = (self.tradingStatusRaw == 'trade')

        self.pool = list(
            set(self.volumeRaw.columns) & set(self.tradingStatus.columns))

        self.nextTradingDate = self.sim_period[-1] if self.sim_period else None
        if self.nextTradingDate:

            self.nextPrice = fetch(self.nextTradingDate, field="price")
            self.nextOpenTWAP = self.nextPrice.iloc[3:40, :].mean()
            self.pool = sorted(list(set(self.nextOpenTWAP.index) & set(self.pool)))

            self.price = self.priceRaw[self.pool]
            self.volume = self.volumeRaw[self.pool]

            self.openTWAP = self.price.iloc[3:40, :].mean()
            self.nextOpenTWAP = self.nextOpenTWAP[self.pool]
            self.nextPrice = self.nextPrice[self.pool]

            self.limitFlag = (
                (self.nextPrice.iloc[-1, :] / self.price.iloc[-1, :] -
                 1).abs() +
                (self.nextPrice.iloc[2, :] / self.price.iloc[-1, :] -
                 1).abs()).fillna(0) < 0.18

            self.limitFlag = self.limitFlag[self.limitFlag.values]

            self.pool = self.limitFlag.index

            self.price = self.price[self.pool]
            self.volume = self.volume[self.pool]

            #print(self.limitFlag.shape, self.price.shape, self.a_.shape)

            self.nextReturn = ((self.nextOpenTWAP - self.openTWAP) /
                               self.openTWAP).fillna(0)
            self.nextReturn = self.nextReturn[self.pool]

        self.recorderPrice.append(self.price)
        self.recorderVolume.append(self.volume)

        if not np.any(self.signal):
            self.signal = self.alpha().fillna(0)
            return

        self.prePool = sorted(list(set(self.signal.index) & set(self.pool)))
        self.preSignal = self.signal[self.prePool]
        self.signal = self.alpha().fillna(0)
        self.history.append(self.preSignal)
        self.treatment()
        self.nextReturn = self.nextReturn[self.prePool]
        self.weights = self.allocate()

    def crossSection(self, how="normal"):
        """
        cross-section normalize
        """
        if how == "normal":
            self.preSignal = ((self.preSignal - self.preSignal.mean()) /
                          self.preSignal.std()).fillna(0)
        elif how == "rank":
            self.preSignal = self.preSignal.rank()/len(self.preSignal)
        else:
            pass 
        
        
    def timeSeris(self):
        """
        Time Series normalize (self clean)
        """
        if len(self.history) < self.historySize:
            return
        df = pd.concat(self.history, axis=1)
        df.fillna(df.mean())
        self.preSignal = ((df.iloc[:, -1] - df.mean(axis=1)) /
                          df.std(axis=1)).loc[self.preSignal.index]
        #print(self.preSignal.isnull().sum())
        #print(self.preSignal.shape)

    def treatment(self):
        """
        self defined treatment
        """
        self.timeSeris()
        self.crossSection()

    def alpha(self):
        """
        Core Strategy Part
        Fields avaiable:
         - self.price
         - self.volume
        """
        ...

    def allocate(self):
        """
        (Should be rewrite) This function assgins different weights of AUM on stocks, default equally allocate on top 20% and buttom 20% stocks (long/short)  
        """
        
        #os.path.join("/mnt/data","data_cache",field)
        alphanum = self.description.split("\n")[0].strip()
        if "/" in alphanum:
            alphanum = alphanum.split("/")[-1][:-3]
            self.preSignal.to_csv("/mnt/shared/public/predict_kai/" + self.now + "-" + alphanum + ".csv")
            
        long_stock = np.where(
            self.preSignal >= np.quantile(self.preSignal, 0.8), self.preSignal,
            -self.positionSmooth) + self.positionSmooth
        short_stock = np.ones_like(long_stock)  # fake index
        return {"long": long_stock, "short": short_stock}

    def run(self, log=True):
        """
        Evaluate of strategy performance, in terms of portfolio return and prediction-reality correlation
        """

        startTime = datetime.datetime.now()
        periodReturn = [1, 1, 1]
        periodWR = [0,0]
        lastYearReturn = 1
        self.update()
        self.log_time = str(datetime.datetime.now())
        with open("./logs/log-{}.csv".format(self.log_time), "w") as output:
            print("date,long,short,excess return,culmulative return",
                  file=output)
            while len(self.sim_period) > 1:
                lastDate = self.now
                self.update()
                #self.preSignal.to_csv("Signal-{}.csv".format(self.now))
                #self.nextReturn.to_csv("{}.csv".format(self.now))

                long_part = (self.weights["long"] * self.nextReturn
                             ).sum() / self.weights["long"].sum()
                short_part = (self.weights["short"] * self.nextReturn
                              ).sum() / self.weights["short"].sum()
                excess_return = long_part - short_part
                self.cum_return *= (1 + excess_return)
                
                
                periodWR[0] += int(excess_return>0)
                periodWR[1] += 1
                
                if self.log:
                    print(self.now,
                          long_part,
                          short_part,
                          excess_return,
                          self.cum_return,
                          sep=",",
                          file=output)
                if self.verbose == 2:
                    print(
                        "[{}]".format(datetime.datetime.now() - startTime),
                        self.now,
                        "  \tlong: {:7.4f}  \tshort: {:7.4f}  \texcess return: {:7.4f}  \tcumulative return: {:7.4f}"
                        .format(long_part, short_part, excess_return,
                                self.cum_return))
                else:
                    if self.now.split("-")[self.verbose] != lastDate.split(
                            "-")[self.verbose]:
                        print(
                            "[{}]".format(datetime.datetime.now() - startTime),
                            lastDate,
                            "excess return: {:7.4f} \tcumulative return: {:7.4f} \twinning rate: {:7.4f}"
                            .format(
                                self.cum_return / periodReturn[self.verbose],
                                self.cum_return,
                                periodWR[0]/periodWR[1]))
                        periodReturn[self.verbose] = self.cum_return
                        periodWR = [0,0]

        with open("./formulas/formula-{}.txt".format(self.log_time),
                  "w") as output:
            output.write(self.description)

        Intraday.evaluate(self.log_time)

    @classmethod
    def evaluate(cls, log_time):
        result = pd.read_csv("./logs/log-{}.csv".format(log_time))
        result["date"] = result["date"].astype(np.datetime64)
        result["historyHigh"] = [
            max(result["culmulative return"][:i + 1])
            for i in range(len(result))
        ]
        result["drawdown"] = 1 - result["culmulative return"] / result[
            "historyHigh"]
        result["year"] = result.date.apply(lambda x: x.year)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax2 = ax.twinx()
        ax2.set(ylim=(0, max(result["drawdown"]) * 2.5))
        ax.plot(result["date"], result["long"].cumsum(), c="red", label="Long")
        ax.plot(result["date"],
                result["short"].cumsum(),
                c="green",
                label="Short(index)")
        ax.plot(result["date"], (result["long"] - result["short"]).cumsum(),
                c="blue",
                label="Hedged")
        ax.legend(bbox_to_anchor=(0.55, 0.78))

        fig.text(0.72,
                 0.3,
                 '$Sharpe= {:.4f}$\n$Daily\ bp={:.4f}$'.format(
                     np.sqrt(252) * result["excess return"].mean() /
                     result["excess return"].std(),
                     result["excess return"].mean() * 10000),
                 fontsize=10)

        ax2.fill_between(result["date"], result["drawdown"], alpha=0.4)
        ax3 = fig.add_axes([.18, .65, .2, .2])
        ax3.hist(result["excess return"],
                 bins=50,
                 density=False,
                 edgecolor="b",
                 alpha=0.6)
        ax3.axvline(x=0, color="red")
        fig.savefig('./graphs/{}.png'.format(log_time))
        fig.show()

        result["factor"] = result["excess return"] + 1
        result["long"] = result["long"] + 1
        result["short"] = result["short"] + 1

        simRes = pd.DataFrame({
                "Sharpe":
                math.sqrt(252) *
                result.groupby("year")["excess return"].mean() /
                result.groupby("year")["excess return"].std(),
                "long":
                result.groupby("year")["long"].prod() - 1,
                "short":
                result.groupby("year")["short"].prod() - 1,
                "bp(hedged)":
                result.groupby("year")["excess return"].mean() * 10000,
                "return": (result.groupby("year")["factor"]).prod() - 1,
                "ir":result.groupby("year")["excess return"].mean() / result.groupby("year")["excess return"].std()
            })

        simRes.loc["Avg."] = pd.Series({
                "Sharpe":
                math.sqrt(252) * result["excess return"].mean() / result["excess return"].std(),
                "long":  result["long"].prod() - 1,
                "short": result["short"].prod() - 1,
                "bp(hedged)": result["excess return"].mean() * 10000,
                "return": (result["factor"]).prod() - 1, 
                "ir":result["excess return"].mean() / result["excess return"].std()
            })
        
        print("\n",simRes,"\n")
        
        
        # result = pd.read_csv("./logs/log-{}.csv".format(log_time))
            
        benchmarks = [
            os.path.join("./alphaResults", f)
            for f in os.listdir("./alphaResults") if f.endswith(".csv")
        ]
        result["date"] = result["date"].astype(str)

        if "SimFlag" not in os.listdir("./alphaResults"):
            corrRes = {}
            bpRes = {}
            irRes = {}
            for bm in benchmarks:
                riskFactor = pd.read_csv(bm)
                riskFactor = riskFactor.query("'{}' < date < '{}'".format(
                    result.date.iloc[0], result.date.iloc[-1]))
                result = result.query("'{}' < date < '{}'".format(
                    result.date.iloc[0], result.date.iloc[-1]))
                corrRes[bm.split("/")[-1].split(".")[0]] = np.corrcoef(
                    riskFactor["excess return"], result["excess return"])[0, 1]
                bpRes[bm.split("/")[-1].split(".")[0]] = riskFactor["excess return"].mean() * 10000
                irRes[bm.split("/")[-1].split(".")[0]] = riskFactor["excess return"].mean() / riskFactor["excess return"].std() 

            res = pd.DataFrame([corrRes,bpRes, irRes], index=["corr","bp", "ir"]).T
            print(res.sort_values(by="corr", ascending=False).round(4))