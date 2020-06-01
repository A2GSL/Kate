import os
import sys
sys.path.append(os.getcwd())

from KATE.AlphaBase import *

class Alpha(Intraday): 
    def __init__(self, sim_start, sim_end, **kwargs):
        super().__init__(sim_start, sim_end, **kwargs)
        self.description = __file__ + "\n" + open(__file__).read()
        self.result = pd.read_csv("sim_result.csv", index_col=0)
        self.factorWeights = (((self.result.rolling(30).sum() - self.result).fillna(0) * 20) + 0.5)**2
        self.alpha_path = "/mnt/shared/public/predict_kai/"
        self.files = os.listdir("/mnt/shared/public/predict_kai/")
        self.factorCorr = pd.read_csv("poolCorr.csv", index_col=0)
        
        self.initFlag = 1
    
    def rename(self, filename):
        num = int(filename.split("alpha")[-1].split(".")[0])
        return "alpha{:03}.py".format(num)

    def genDaily(self):
        #sorted([rename(i) for i in sim_daily])
        sim_daily = [f for f in self.files if f.startswith(self.now)]
        symbol = pd.read_csv(self.alpha_path+sim_daily[0]).sort_values(by = "Symbol")["Symbol"].values
        return pd.DataFrame({self.rename(alpha): pd.read_csv(self.alpha_path+alpha).sort_values(by = "Symbol").iloc[:,1].values for 
                             alpha in sim_daily}).sort_index(axis=1), symbol

    def construct(self):
    
        corr = np.where(self.factorCorr > 0.99, 0, self.factorCorr)
        values = ((self.factorWeights.loc[[self.now]] * (
                np.array([1 - sum(sorted(c, reverse=True)[:2])/2 for c in corr]) 
                                                        )
                  ).values @ self.genDaily()[0].T.values)
        return pd.Series(values[0], index=self.genDaily()[1])

        
    def alpha(self):
        
        if self.initFlag:
            self.initFlag = 0
            return self.price.mean()
        
        self.preSignal = self.construct()#[self.price.columns]
        return self.price.mean()
       
    
    def treatment(self):
        """
        self defined treatment
        """
        self.crossSection(how = "rank")
    
        
if __name__ == "__main__":
    agent = Alpha("2015-01-05", "2020-05-08", verbose = 1)
    agent.run()
    
