touch ./alphaResults/SimFlag
for filename in ./alphaPools/*.py; do
    python $filename &
done
sleep 120m
python ./KATE/poolCorr.py
rm ./alphaResults/SimFlag