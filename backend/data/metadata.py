# abbreviated column names in csv file to MySQL table column names
column_mapping = {
    'gvkey': 'company_id',
    'tic': 'ticker',
    'conm': 'company_name',
    'gind': 'industry_code',
    'loc': 'country',
    'fyear': 'year',

    'act': 'current_assets',
    'at': 'total_assets',
    'ch': 'cash',
    'dlc': 'current_debt',
    'dltt': 'long_term_debt',
    'icapt': 'invested_capital',
    'lt': 'total_liabilities',
    'cogs': 'cost_of_goods_sold',
    'ebit': 'ebit',
    'ebitda': 'ebitda',
    'epsfx': 'eps',
    'ni': 'net_income',
    'revt': 'total_revenue',
    'txt': 'income_taxes',
    'xint': 'interest_expense',
    'capx': 'capital_expenditures',
    'fincf': 'net_cash_flow_financing',
    'ivncf': 'net_cash_flow_investing',
    'oancf': 'net_cash_flow_operating',
    'csho': 'common_shares_outstanding',
    'teq': 'total_equity',
    'dvpsx_f': 'dividends_per_share',
    'mkvalt': 'market_value',
    'prcc_f': 'price',
    'gp': 'gross_profit'
}


# Derived financial columns we will calculate
derived_columns = [
    'revenue_growth', 
    'eps_growth', 
    'dividend_growth', 
    'net_profit_margin',
    'operating_margin', 
    'gross_margin', 
    'return_on_assets',
     'return_on_equity',
    'return_on_invested_capital', 
    'free_cash_flow', 
    'free_cash_flow_margin',
    'debt_to_equity', 
    'debt_to_assets', 
    'price_to_earnings_ratio',
    'price_to_book_ratio', 
    'price_to_share_ratio', 
    'EV_to_EBITDA_ratio'
]