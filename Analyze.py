import os
import pandas as pd

poolSize = len([f for f in os.listdir("alphaPools/") if f.endswith("py")])
logfiles = [os.path.join("/home/highfort/project/logs", f) for f in sorted(os.listdir("logs/"), reverse=True)[:poolSize]]
formulas = [os.path.join("/home/highfort/project/formulas", f) for f in sorted(os.listdir("formulas/"), reverse=True)[:poolSize]]

def getAlphaNum(filename):
    with open(filename) as f:
        alpha = f.readline()
    return "alpha{:03}".format(int(alpha.strip().split("/")[-1].split(".")[0][5:]))


for i in range(poolSize):
    log = pd.read_csv(logfiles[i])
    log.to_csv("/home/highfort/project/alphaResults/{}.csv".format(getAlphaNum(formulas[i])))
    
    
result = pd.DataFrame({getAlphaNum(formulas[i]): pd.read_csv(logfiles[i])["excess return"] for i in range(poolSize)}).sort_index(axis=1)
corrs = result.corr()
corrs.to_csv("poolCorr.csv")
print(corrs.round(3))

