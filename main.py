import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pandas_ta as ta

dfs = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
list_of_stocks = dfs[0].Symbol
list_of_stocks.head()

len(list_of_stocks)
st.write("""
The Content is for informational purposes only, you should not construe any such information or other material as investment, financial, or other advice.
""")
ticker = st.selectbox("Select stock", list_of_stocks)
ticker

stock = yf.Ticker(ticker)
stock.history().head(3)
# stock.earnings
stock_name = stock.info['longName']

period = "1y"
interval = "1d"
# valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
# valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo

stock_price = stock.history(period=period, interval=interval).drop(['Stock Splits', 'Dividends'], axis=1)


#Stock price and volume.


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [4, 1]})
ax1.set(title="Stock price chart of " + stock_name)
ax1.plot(stock_price.index, stock_price.Close, color="g")
ax1.grid(axis='y', ls='--')
ax2.set(title="Stock trade volume")
ax2.bar(stock_price.index, stock_price.Volume, color="blue")
# plt.show()
st.pyplot(fig)


#Exponentially Weighted Moving Average


ewma_range = [10, 30, 100]
for ewma in ewma_range:
    stock_price[f'EWMA_{ewma}'] = stock_price['Close'].ewm(span=ewma, adjust=False).mean()

fig, ax = plt.subplots(figsize=(15, 7))
ax.plot(stock_price.index, stock_price.Close, label="Closing price")

for ewma in ewma_range:
    ax.plot(stock_price.index, stock_price[f'EWMA_{ewma}'], label=f"EWMA {ewma}")

ax.grid(axis='y', ls='--')
ax.set_title("Exponentially Weighted Moving Average")
plt.legend(loc="upper left")
# plt.show()
st.pyplot(fig)


#Relative Strength Index (RSI)


stock_price['RSI_14'] = ta.rsi(stock_price['Close'], lenght=14)
hor70 = [70 for price in stock_price['RSI_14']]
hor30 = [30 for price in stock_price['RSI_14']]

fig, ax = plt.subplots(figsize=(15, 5))
ax.plot(stock_price.index, stock_price['RSI_14'])
ax.plot(stock_price.index, hor70, ls='--', c='r')
ax.plot(stock_price.index, hor30, ls='--', c='g')
ax.set_title('Relative Strength Index (RSI)')
plt.ylim(15, 85)
# plt.show()
st.pyplot(fig)


# Moving Average Convergence / Divergence (MACD)


MACD = ta.macd(stock_price['Close'], fast=12, slow=26, signal=9)
stock_price = pd.concat([stock_price, MACD], axis=1)

fig, ax = plt.subplots(figsize=(15, 5))
ax.bar(stock_price.index, stock_price['MACDh_12_26_9'])
ax.plot(stock_price.index, stock_price['MACDs_12_26_9'], c='g')
ax.plot(stock_price.index, stock_price['MACD_12_26_9'], c='r')
ax.grid(axis='y', ls='--')
ax.set_title('Moving Average Convergence / Divergence (MACD)')
# plt.show()
st.pyplot(fig)


# Stochastic Oscillator


STOCH = ta.stoch(high=stock_price.High, low=stock_price.Low, close=stock_price.Close)
stock_price = pd.concat([stock_price, STOCH], axis=1)
hor80 = [80 for price in stock_price['STOCHd_14_3_3']]
hor20 = [20 for price in stock_price['STOCHd_14_3_3']]
fig, ax = plt.subplots(figsize=(15, 5))
ax.plot(stock_price.index, stock_price['STOCHd_14_3_3'], label='%D')
ax.plot(stock_price.index, stock_price['STOCHk_14_3_3'], label='%K')
ax.plot(stock_price.index, hor20, ls=':', c='g')
ax.plot(stock_price.index, hor80, ls=':', c='r')
ax.set_title('Stochastic Oscillator')
plt.legend(loc='upper left')
# plt.show()
st.pyplot(fig)


# Bollinger Bands


bbands = ta.bbands(stock_price.Close, length=20, std=2)
bbands.tail(2)
stock_price = pd.concat([stock_price, bbands], axis=1)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 13), gridspec_kw={'height_ratios': [2, 1, 1]})
ax1.plot(stock_price.Close, ls='--', c='k', label='Stock price')
ax1.plot(stock_price['BBL_20_2.0'], c='g', label='lowerBB')
ax1.plot(stock_price['BBM_20_2.0'], c='b', label='middleBB')
ax1.plot(stock_price['BBU_20_2.0'], c='r', label='upperBB')
ax1.legend(loc='upper left')
ax1.grid(axis='y', ls='--')
ax1.set_title('Bollinger Bands')
ax2.plot(stock_price['BBP_20_2.0'])
ax2.grid()
ax2.set_title('%b')
ax3.plot(stock_price['BBB_20_2.0'])
ax3.grid()
ax3.set_title('Bandwidth')
# plt.show()
st.pyplot(fig)


# Recommendataion output


names = ["EWMA", "RSI", "MACD", "STOCH", "BBounds"]


def stock_recommendation(stock):
    signals = []
    # EWMA
    if (stock[-1:]['EWMA_10'] > stock[-1:]['EWMA_30']).bool() and (
            stock[-1:]['EWMA_30'] > stock[-1:]['EWMA_100']).bool():
        signals.append(1)
    elif (stock[-1:]['EWMA_10'] < stock[-1:]['EWMA_30']).bool() and (
            stock[-1:]['EWMA_30'] < stock[-1:]['EWMA_100']).bool():
        signals.append(-1)
    else:
        signals.append(0)
    # RSI
    if (stock[-1:]['RSI_14'] > 70).bool():
        signals.append(-1)
    elif (stock[-1:]['RSI_14'] < 30).bool():
        signals.append(1)
    else:
        signals.append(0)
    # MACD
    if (stock[-1:]['MACDh_12_26_9'] > 0).bool():
        signals.append(1)
    else:
        signals.append(-1)
    # STOCH
    if (stock[-1:]['STOCHk_14_3_3'] > 80).bool() or (stock[-1:]['STOCHd_14_3_3'] > 80).bool():
        signals.append(-1)
    elif (stock[-1:]['STOCHk_14_3_3'] < 20).bool() or (stock[-1:]['STOCHd_14_3_3'] < 20).bool():
        signals.append(1)
    else:
        signals.append(0)
    # BBounds
    if (stock[-1:]['Close'] < stock[-1:]['BBL_20_2.0']).bool():
        signals.append(1)
    elif (stock[-1:]['Close'] > stock[-1:]['BBU_20_2.0']).bool():
        signals.append(-1)
    else:
        signals.append(0)

    return signals


recommendation = stock_recommendation(stock_price)
st.write("Results from individual sub-strategies (-1 = sell, 0 = neutral, 1 = buy): ")
for i in range(len(names)):
    st.write(names[i], recommendation[i])
st.write("Final reccomendation score: ", sum(recommendation))

if sum(recommendation) >= 1:
    st.write("You can consider buying this stock.")
elif sum(recommendation) <= -1:
    st.write("You can consider short selling this stock")
else:
    st.write("Signal is neutral. You can consider looking for a better alternative.")
