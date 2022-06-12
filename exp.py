import pandas

file = pandas.read_csv("sp_500_stocks.csv")

for t in file['Ticker']:
    print(t)