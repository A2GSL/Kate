import os
import pandas as pd

poolSize = len([f for f in os.listdir("alphaPools/") if f.endswith("py")])
logfiles = [os.path.join("/home/project/logs", f) for f in sorted(os.listdir("logs/"), reverse=True)[:poolSize]]
formulas = [os.path.join("/home/project/formulas", f) for f in sorted(os.listdir("formulas/"), reverse=True)[:poolSize]]
date = pd.read_csv(logfiles[0])["date"].values

def getAlphaNum(filename):
    with open(filename) as f:
        alpha = f.readline()
    return "alpha{:03}".format(int(alpha.strip().split("/")[-1].split(".")[0][5:]))


for i in range(poolSize):
    log = pd.read_csv(logfiles[i])
    log.to_csv("/home/project/alphaResults/{}.csv".format(getAlphaNum(formulas[i])))
    
    
result = pd.DataFrame({getAlphaNum(formulas[i]): pd.read_csv(logfiles[i])["excess return"] for i in range(poolSize)}).sort_index(axis=1)
corrs = result.corr()
corrs.to_csv("poolCorr.csv")
print(corrs.round(3))

result = pd.DataFrame({getAlphaNum(formulas[i]): 
                       pd.read_csv(logfiles[i])["excess return"] for i in range(poolSize)}).sort_index(axis=1).set_index(date).round(5)

result.to_csv("sim_result.csv")

