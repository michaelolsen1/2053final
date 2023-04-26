#Michael Olsen, Liz Borao, Lam Dinh

#import statements
import requests
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

#API Information and Global Variables_________________________________________________________________________________________
#Price History Time Periods
PERIODS = ['5d', '1mo', '3mo', '6mo', 'ytd', '1y', '5y']

#For the Ratio Analysis Option
METRICS = ['currentRatioTTM', 'quickRatioTTM', 'cashRatioTTM', 'debtEquityRatioTTM', 'netProfitMarginTTM', 'operatingProfitMarginTTM', 
'returnOnAssetsTTM', 'returnOnEquityTTM', 'peRatioTTM', 'priceToBookRatioTTM', 'priceToSalesRatioTTM', 'enterpriseValueMultipleTTM', 
'dividendYielPercentageTTM']

TABLELABELS = ['Current Ratio (x)', 'Quick Ratio (x)', 'Cash Ratio (x)', 'Debt/Equity (x)', 'Net Margin', 'Operating Margin', 
'Return on Assets', 'Return on Equity', 'P/E (x)', 'Price/Book (x)', 'Price/Sales (x)', 'EV/EBITDA (x)', 'Dividend Yield (%)']

#Stock Overview API
alphakey = "II47TTJUVC09QJXF"
alphaURL = "https://www.alphavantage.co/query"

#Ratios API
#"TICKER" must be replaced with a stock symbol
fmpURL = "https://financialmodelingprep.com/api/v3/ratios-ttm/TICKER?apikey=2495d3c2d054633406c1bb712f9dfa58"

#Comparable Companies API
#"TICKER" must be replaced with a stock symbol
polygonURL = "https://api.polygon.io/v1/meta/symbols/TICKER/company?apiKey=yjCuOs_eDEQQZbHywa3FS7ISycf0M3x2"

#News Stories API
newskey = "a9fac7f2c981432fadd2843a09eccaf8"
newsURL = "https://newsapi.org/v2/everything?language=en"

#function definitions_________________________________________________________________________________________________________-
def getURLdata(url,options=''):
    try:
        response = requests.get(url,options)
        if response.status_code != 200:
            raise
        data = response.json()
        return data
    except:
        #print("API call was not successful.") #Commented out for appearance to user.
        return None

def getPolydata(url, ticker):
    newurl = url.replace("TICKER", ticker)
    return getURLdata(newurl)

def overview(stockdata):
    print(stockdata['Name'], " (", stockdata['Exchange'], ": ", stockdata["Symbol"], ") ",sep="")
    print("Sector:", stockdata['Sector'])
    print("Industry:", stockdata['Industry'])
    print("Market Cap:", '${:,.0f}'.format(float(stockdata['MarketCapitalization'])))
    print("Last Quarter Ended:", stockdata['LatestQuarter'])

def news(newsdata, ticker):
    print("News Articles Involving ", ticker, ":", sep="")
    for x in newsdata['articles']:
        print(x['title'])
        print(x['url'])
        print("Source:", x['source']['name'])
        print(x['publishedAt'])
        print("")

def getRatios(ticker):
    ratios = []
    try:
        data = getPolydata(fmpURL, ticker)[0]
        if data['netProfitMarginTTM'] == None:
            return None
    except:
        return None
    else:
        for x in METRICS:
            ratios.append(data[x])
        return ratios
    
    

#Main Application___________________________________________________________________________________________________________
while True:
    while True:
        ticker = input("Enter a stock ticker: ").upper()
        overopts = {'function': 'OVERVIEW', 'symbol': ticker, 'apikey': alphakey}
        stockOverview = getURLdata(alphaURL, overopts)
        if len(stockOverview) <= 1:
            print("Company Not Found.")
        else:
            print("")
            overview(stockOverview)
            print("")
            break 
    while True:
        while True:
            print("What Information would you like to see?")
            choice = input("'C' to Compare Price with Other Stocks, 'R' for Ratio Analysis, 'N' for News: ").upper()
            if not choice in "CRN":
                print('Invalid Information Choice')
            else:
                print("")
                break

        #NEWS
        if choice == "N":
            newsopts = {'q': stockOverview['Name'], 'qInTitle': [ticker, stockOverview['Name']], 'pageSize': 10, 'page': 1, 'apiKey': newskey}
            newsdata = getURLdata(newsURL, newsopts)
            news(newsdata, ticker)

        #RATIO ANALYSIS
        if choice == "R":
            comps = getPolydata(polygonURL, ticker)['similar']
            if len(comps) > 5:
                comps = comps[0:5]
            comps.insert(0,ticker)

            compLists = []
            usableComps = []
            for x in comps:
                lst = getRatios(x)
                if lst != None:
                    compLists.append(lst)
                    usableComps.append(x)

            print("Ratio Analysis:", ticker, "and Comparable Firms")
            df = pd.DataFrame(compLists,columns=TABLELABELS)
            df.index = usableComps
            df = df.transpose()
            for column in df:
                df[column] = pd.to_numeric(df[column], errors="coerce")
            avgs = df.mean(axis=1)
            df["Average"] = avgs
            print(df)

        #PRICE COMPARISONS
        if choice == "C":
            while True:
                timespan = input("Time Period (5d, 1mo, 3mo, 6mo, YTD, 1y, 5y): ").lower()
                if timespan in PERIODS:
                    break
                else:
                    print("Invalid Time Period.")
            pricedf = yf.Ticker(ticker).history(period=timespan)
            pricedf.drop(['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'], axis=1, inplace=True)
            pricedf.rename(columns={'Close': ticker}, inplace=True)
            pricedf[ticker] = pricedf.apply(lambda row: round(row[ticker], 2), axis=1)
            print("Enter The stocks that you would like to compare to ", ticker, " (3 MAX):", sep="")
            print("Enter 'DONE' to stop entering stocks.")
            numTickers = 0
            while numTickers < 3:
                print("")
                userin = input("Stock " + str(numTickers+1) + ": ").upper()
                if userin == "DONE":
                    break
                tick = yf.Ticker(userin)
                data = tick.history(period=timespan)
                if len(data) != 0:
                    print("You entered ", userin, ".", sep="")
                    numTickers+=1
                    data.rename(columns={'Close': userin}, inplace=True)
                    pricedf[userin] = data[userin]
                    pricedf[userin] = pricedf.apply(lambda row: round(row[userin], 2), axis=1)
            
            pricedf.plot()
            plt.title("Stock Price History: " + ticker + " and Comparable Firms")
            plt.ylabel("Price at Close (USD)")
            plt.grid(b=True, which='major', axis='both')
            plt.show(block=False)
        
        #Get more information about the entered stock.
        print("")
        answer = input("Press 'Y' for more information about " + ticker +  " (any other key to exit). ")
        if answer.upper() != "Y":
            break
    #Enter a new stock
    print("")
    ans = input("Press 'Y' to enter another stock (any other key to exit). ")
    if ans.upper() != "Y":
            print("Session Terminated.")
            break
    
