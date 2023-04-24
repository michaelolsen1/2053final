#Michael Olsen 
#001

#Import Statements___________________________________________________________________________________________________________________
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from pandastable import Table
import yfinance as yf
from tkinter import Button, Entry, Frame, Label, OptionMenu, StringVar, Tk
from tkinter import messagebox
import webbrowser

#API Information and Constants_______________________________________________________________________________________________________
#For the Ratio Analysis Option
METRICS = ['currentRatioTTM', 'quickRatioTTM', 'cashRatioTTM', 'debtEquityRatioTTM', 'netProfitMarginTTM', 'operatingProfitMarginTTM', 
'returnOnAssetsTTM', 'returnOnEquityTTM', 'peRatioTTM', 'priceToBookRatioTTM', 'priceToSalesRatioTTM', 'enterpriseValueMultipleTTM', 
'dividendYielPercentageTTM']

TABLELABELS = ['Current Ratio (x)', 'Quick Ratio (x)', 'Cash Ratio (x)', 'Debt/Equity (x)', 'Net Margin', 'Operating Margin', 
'Return on Assets', 'Return on Equity', 'P/E (x)', 'Price/Book (x)', 'Price/Sales (x)', 'EV/EBITDA (x)', 'Dividend Yield (%)']

#Stock Overview API
alphakey = "II47TTJUVC09QJXF"
alphaURL = "https://www.alphavantage.co/query"

#Ratios API - Key included in URL
#"TICKER" must be replaced with a stock symbol
fmpURL = "https://financialmodelingprep.com/api/v3/ratios-ttm/TICKER?apikey=2495d3c2d054633406c1bb712f9dfa58"

#Comparable Companies API - Key included in URL
#"TICKER" must be replaced with a stock symbol
polygonURL = "https://api.polygon.io/v1/meta/symbols/TICKER/company?apiKey=yjCuOs_eDEQQZbHywa3FS7ISycf0M3x2"

#News Stories API
newskey = "aef8f3fe00bd49b78c1955e31ebd7588"
newsURL = "https://newsapi.org/v2/everything?language=en"

#Function Definitions________________________________________________________________________________________________________________
#Uses the requests module to return data obtained from a given URL
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

#Formats API URLs that contain the company stock symbol within the URL instead of within the options
#Returns getURLdata() for the new URL containing the 'stock' parameter
def getPolydata(url, stock, opts=""):
    newurl = url.replace("TICKER", stock)
    return getURLdata(newurl, opts)

#Takes a Frame parameter and clears all widgets from it
def clearframe(frm):
    for widg in frm.winfo_children():
            widg.pack_forget()

#Takes a stock ticker as a parameter and checks whether it is valid (found in the Alpha Vantage API)
#Displays general information of a valid stock and calls the infoChoice() method.
def enterStock(stock):
    overopts = {'function': 'OVERVIEW', 'symbol': stock, 'apikey': alphakey}
    stockOverview = getURLdata(alphaURL, overopts)
    try:
        clearframe(g)
        clearframe(f)
        global companySymbol
        companySymbol = stockOverview['Symbol']
        global companyName
        companyName = stockOverview['Name']
        Label(g, text="").pack()
        Label(g, text=companyName + " (" + stockOverview['Exchange'] + ": " + companySymbol + ") ").pack()
        Label(g, text="Sector: " + stockOverview['Sector']).pack()
        Label(g, text="Industry: " + stockOverview['Industry']).pack()
        Label(g, text="Market Cap: " + '${:,.0f}'.format(float(stockOverview['MarketCapitalization']))).pack()
        Label(g, text="").pack()
        g.pack()
    except:
        messagebox.showinfo(title="Invalid Input",message="Company Not Found.").pack()
    else:
        infoChoice() 

#Creates an OptionMenu so the user may choose from News, Ratio Analyses, and Price Comparisons for the entered stock.
def infoChoice():
    Label(g, text="What information would you like to see?").pack()
    var = StringVar(g)
    var.set("News")
    choices = OptionMenu(g, var, "News", "Ratio Analysis", "Compare Prices")
    choices.pack()
    Button(g, text="ENTER",command=lambda: getInfo(var.get()), cursor="hand2").pack()
    Label(g,text="").pack()

#Takes the infoChoice() choice and calls the corresponding function.
def getInfo(v):
    clearframe(f)
    if v == "News":
        getPageCount()
    elif v == "Ratio Analysis":
        ratioAnalysis()
    else:
        getTimespan()
    f.pack()

#Begins the process of obtaining news articles by calculating the pages needed to display the articles (5 articles per page)
def getPageCount():
    try:
        data = getNewsData()
        pgct = -1*(data['totalResults'] // -5)
    except:
        Label(f,text="News for this stock is currently unavailable.").pack()
    else:
        if pgct > 3:
            news(1, 3, data)
        else:
            news(1, pgct, data)

#Takes a page as a parameter and returns news article data for that page
def getNewsData(pg=1):
    searchwords = [companyName]
    #Searching for one-letter symbols (i.e. Ford - F) often produces irrelevant article results.
    if len(companySymbol) > 1:
        searchwords.append(companySymbol)
    newsopts = {'q': searchwords, 'pageSize': 5, 'page': pg, 'apiKey': newskey}
    newsdata = getURLdata(newsURL, newsopts)
    return newsdata

#Pulls a list of articles from the News API, displays them, and links their URLs to their web pages
def news(pg, pgcount, newsdata=None):
    clearframe(f)
    if newsdata == None:
        newsdata = getNewsData(pg)
    Label(f,text="News Articles Involving " + companyName + ":").pack()
    weblinks = []
    urls = []
    for x in newsdata['articles']:
        Label(f, text=x['title']).pack()
        link = Label(f,text=x['url'], fg='blue', cursor='hand2')
        weblinks.append(link)
        weblinks[len(weblinks)-1].pack()
        urls.append(x['url'])
        Label(f,text=x['publishedAt'] + ", Source: " + x['source']['name']).pack()
        Label(f,text="").pack()
    Label(f,text="Page " + str(pg) + " of " + str(pgcount)).pack()
    #Linking each URL
    for n in range(len(urls)):
        weblinks[n].bind("<Button-1>", lambda lam, text=urls[n]: gotoURL(text))
    #Page Turning
    if pg < pgcount:
        Button(f,text="NEXT",command=lambda: news(pg+1, pgcount)).pack()
    if pg > 1:
        Button(f,text="BACK",command=lambda: news(pg-1, pgcount)).pack()

#Takes a URL as a parameter and uses the webbrowser module to open the corresponding site page
def gotoURL(url):
    webbrowser.open_new(url)

#Begins the Ratio Analysis process by obtaining a list of comparable companies from the Polygon.io API
#Calls getRatios() to get a list of ratios for each stock and sends a list of these lists to the makeTable() function
def ratioAnalysis():
    try:
        comps = getPolydata(polygonURL, companySymbol)['similar']
    except:
        Label(f,text="Ratio Analysis for this stock is currently unavailable.").pack()
    else:
        if len(comps) > 5:
            comps = comps[0:5]
        comps.insert(0,companySymbol)

        compLists = []
        usableComps = []
        for x in comps:
            lst = getRatios(x)
            if lst != None:
                compLists.append(lst)
                usableComps.append(x)
        makeTable(compLists, usableComps)

#Constructs a Pandas DataFrame from the list of ratio lists created in ratioAnalysis()
#Constructs a Pandas Table from the DataFrame and displays it
def makeTable(compLists, usableComps):
    Label(f, text="Ratio Analysis: " + companyName + " and Comparable Firms").pack()
    df = pd.DataFrame(compLists,columns=TABLELABELS)
    df.index = usableComps
    df = df.transpose()
    for column in df:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    avgs = df.mean(axis=1)
    df["Average"] = avgs
    temp = Frame(f)
    temp.pack()
    tbl = Table(temp, dataframe=df, editable=False)
    tbl.showIndex()
    tbl.show()

#Takes a stock symbol as a parameter and obtains the ratios listed in METRICS for it; returns the ratios as a list
def getRatios(stock):
    ratios = []
    try:
        data = getPolydata(fmpURL, stock)[0]
        if data['netProfitMarginTTM'] == None:
            return None
    except:
        return None
    else:
        for x in METRICS:
            ratios.append(data[x])
        return ratios

#Begins the Price Comparison process by displaying an option menu for the time period of the price graph
#calls getPriceComps() and sends the OptionMenu selection as a parameter
def getTimespan():
    Label(f, text="What time period would you like to see?").pack()
    var = StringVar(f)
    var.set("YTD")
    choices = OptionMenu(f, var, '5d', '1mo', '3mo', '6mo', 'YTD', '1y', '5y')
    choices.pack()
    Button(f, text="ENTER",command=lambda: getPriceComps(var.get()), cursor="hand2").pack()
    Label(f,text="").pack()

#Builds the price Dataframe and prompts the user to enter stocks for comparison (see addStocks())    
def getPriceComps(time):
    clearframe(f)
    Label(f,text="You selected " + time + ".").pack()
    pricedf = yf.Ticker(companySymbol).history(period=time)
    pricedf.drop(['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'], axis=1, inplace=True)
    pricedf.rename(columns={'Close': companySymbol}, inplace=True)
    pricedf[companySymbol] = pricedf.apply(lambda row: round(row[companySymbol], 2), axis=1)
    Label(f,text="Enter The stocks that you would like to compare to " + companySymbol + " (3 MAX):").pack()
    Label(f,text="Enter 'DONE' to stop entering stocks.").pack()
    e = Entry(f)
    e.pack()
    Button(f, text="ADD", command=lambda: addStocks(pricedf, time, e.get().upper()), cursor="hand2").pack()

#Pulls data from the yfinance module for each stock; if valid, adds the data to the DataFrame; if done, call makeGraph()
#Sends an error message if stock is invalid or has already been added
def addStocks(df, time, stock):
    if stock == "DONE":
        makeGraph(df)
    else:
        tick = yf.Ticker(stock)
        data = tick.history(period=time)
        if len(data) == 0 or stock in df.columns:
            messagebox.showinfo(title="Invalid Input",message="Company Either Already Added or Not Found.").pack()
        else:
            Label(f,text="You added " + stock + ".").pack()
            data.rename(columns={'Close': stock}, inplace=True)
            df[stock] = data[stock]
            df[stock] = df.apply(lambda row: round(row[stock], 2), axis=1)
    if len(df.columns) == 4:
        makeGraph(df)

#Takes a DataFrame parameter and creates a graph using matplotlib's Figure and FigureCanvasTkAgg; displays graph on GUI
def makeGraph(df):
    print(df.head(6))
    clearframe(f)
    fig = plt.Figure(figsize=(8,5))
    a = fig.add_subplot()
    canv = FigureCanvasTkAgg(fig, f)
    canv.get_tk_widget().pack()
    df.plot(kind='line', legend=True, ax=a, grid=True)
    a.set_title("Stock Price History: " + companyName + " and Comparable Firms")
    a.set_ylabel("Price at Close (USD)")


#Main Application____________________________________________________________________________________________________________________
win = Tk()
win.geometry("1200x600")
win.title("Stock Information App")

#Stock Input
Label(win, text="Enter a Stock Ticker.").pack()
ticker = Entry(win)
ticker.pack()
stockbutton = Button(win,text="ENTER",command=lambda: enterStock(ticker.get().upper()), cursor="hand2")
stockbutton.pack()

#Frame for General Stock Overview and Information Dropdown Menu
g = Frame(win)

#Frame for specific information selected by dropdown menu
f = Frame(win)

win.mainloop()