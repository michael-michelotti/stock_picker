import matplotlib.pyplot as plt


def configure_rc_params(chart_type):
    """
    Takes in a "chart type" string and returns an updated rcParams unique to that chart type. Currently only supports
    "full_chart" chart type, which includes Price, Dividend, Revenue, EPS, and Balance Sheet information
    :param chart_type: String that indicates what type of chart the user will be making
    :return: Returns a matplotlib.pyplot.rcParams object with parameters according to the input string
    """
    if chart_type == 'full_chart':
        my_params = plt.rcParams
        my_params["axes.grid"] = True
        my_params["axes.spines.top"] = False
        my_params["axes.ymargin"] = 0.1
        my_params["figure.figsize"] = [20, 10]
        my_params["font.family"] = ['font.monospace']
        return my_params


def create_chart(chart_type):
    """
    Takes in a "chart type" string and returns a Matplotlib Figure object based on desired format from the "chart_type"
    argument. Currently only supports "full_chart", which includes five axes for Price, Dividend, Revenue, Balance
    Sheet, and EPS data respectively.
    :param chart_type: String that indicates what type of chart the user will be making
    :return: Returns a Matplotlib "Figure" object, with axes according to input string
    """
    if chart_type == 'full_chart':
        fig = plt.figure()
        ax1 = plt.subplot2grid(shape=(2, 2), loc=(0, 0), rowspan=1, colspan=2, fig=fig)
        ax1.set(xlabel='Year (YYYY)',
                ylabel='Price per Share (USD)')
        ax2 = ax1.twinx()
        ax2.set(ylabel='Quarterly Dividends Paid (%)')
        ax3 = plt.subplot2grid(shape=(2, 2), loc=(1, 0), rowspan=1, colspan=1, fig=fig)
        ax3.set(xlabel='Date (YYYY-MM)',
                ylabel='Millions (USD)',
                title='Balance Sheet Information')
        ax4 = plt.subplot2grid(shape=(2, 2), loc=(1, 1), rowspan=1, colspan=1, fig=fig)
        ax4.set(xlabel='Date (YYYY-MM)',
                ylabel='Millions (USD)',
                title='Earnings Information')
        ax5 = ax4.twinx()
        ax5.set(ylabel='Earnings Per Share Quarterly (USD)')
        return fig


def chart_financials(ticker, fig):
    """
    Takes in a "Ticker" object and a Matplotlib "Figure" object (must have five axes). Plots Price, Dividend, Revenue,
    Balance Sheet, and EPS data for the given Ticker.
    :param ticker: "Ticker" object with its price and financials already run
    :param fig: Matplotlib Figure object, which must have five axes
    :return: None
    """
    fig.suptitle(f'{ticker.symbol} Stock Information')
    ax1 = fig.get_axes()[0]
    ax1.plot(ticker.price, label='Price')
    ax1.legend(loc=(0, 0.8))
    if not ticker.dividends.empty:
        ax2 = fig.get_axes()[1]
        ax2.plot(ticker.dividends, color='g', label='Dividend')
        ax2.legend(loc=(0, 0))
    else:
        ax1.text(x=0, y=0, s=f'{ticker.symbol} pays no dividends.')

    # The second plot will have to do with the Balance Sheet, so I will just be plotting the short term/long term assets
    # and the short term/long term liabilities
    ax3 = fig.get_axes()[2]
    ax3.plot(ticker.balance_sheet['ShortTermAssets'] / 10**6, label='ShortTermAssets')
    ax3.plot(ticker.balance_sheet['TotalAssets'] / 10**6, label='TotalAssets')
    ax3.plot(ticker.balance_sheet['ShortTermLiabilities'] / 10**6, label='ShortTermLiabilities')
    ax3.plot(ticker.balance_sheet['TotalLiabilities'] / 10**6, label='TotalLiabilities')
    ax3.legend(loc=(0, 0))

    # The third plot will have to do with EPS and revenues, plotted on the same chart, with differing y scales
    ax4 = fig.get_axes()[3]
    ax4.plot(ticker.income_statement['TotalRevenue'] / 10**6, label='Revenue (Ann.)')
    ax4.plot(ticker.income_statement['NetIncome'] / 10**6, label='Income (Ann.)')
    ax4.legend(loc=(0, 0))

    ax5 = fig.get_axes()[4]
    ax5.plot(ticker.eps['EPS'], label='EPS (Qtrly)', color='g')
    ax5.legend(loc=(0.9, 0))

    plt.savefig(f'charts/{ticker.symbol}.png')
    plt.close(fig)


if __name__ == '__main__':
    plt.rcParams = configure_rc_params('full_chart')
    fig = create_chart('full_chart')
    print('This .py file is intended to be a module, and should not be run directly.')
