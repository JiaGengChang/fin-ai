import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import Tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import sys

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize Langchain model
model = init_chat_model("gpt-4o-mini", model_provider="openai", max_tokens=2000, temperature=0.3)

# Memory saver for agent to remember chat history
memory = MemorySaver()

# Define database connection and tools
db = SQLDatabase.from_uri("mysql+mysqlconnector://root:t0220975b@localhost:3306/financial_db")
query_sql_tool = QuerySQLDatabaseTool(db=db)
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with print(...).",
    func=PythonREPL().run,
)

tools = [query_sql_tool, repl_tool]

# Create agent executor
agent_executor = create_react_agent(model, tools, checkpointer=memory)

# Define the column description
column_description = """
The company_data table in the financial_db MySQL database contains the following columns:

### Company Metadata and Financial Data
1. **company_id (ID)**: Unique identifier for the company.
2. **ticker (TICKER)**: The stock ticker symbol of the company.
3. **company_name (NAME)**: Full name of the company.
4. **country (COUNTRY)**: The country where the company is based.
5. **industry_code (IND_CODE)**: Numeric code representing the company's industry classification.
6. **year (YEAR)**: The fiscal year of the financial data.

### Base Financial Data
7. **current_assets (CURRENT_ASSETS)**: The company's current assets.
8. **total_assets (TOTAL_ASSETS)**: The company's total assets.
9. **cash (CASH)**: The company's cash on hand.
10. **current_debt (CURRENT_DEBT)**: The company's current debt.
11. **long_term_debt (LTD)**: The company's long-term debt.
12. **invested_capital (INVESTED_CAPITAL)**: The company's total invested capital.
13. **total_liabilities (TOTAL_LIABILITIES)**: The company's total liabilities.
14. **cost_of_goods_sold (COGS)**: The cost of goods sold.
15. **ebit (EBIT)**: Earnings before interest and taxes.
16. **ebitda (EBITDA)**: Earnings before interest, taxes, depreciation, and amortization.
17. **eps (EPS)**: Earnings per share.
18. **net_income (NET_INCOME)**: The company's net income.
19. **total_revenue (TOTAL_REVENUE)**: The company's total revenue.
20. **income_taxes (INCOME_TAXES)**: Income taxes.
21. **interest_expense (INTEREST_EXPENSE)**: The company's interest expenses.
22. **capital_expenditures (CAPEX)**: The company's capital expenditures.
23. **net_cash_flow_financing (NET_CASH_FLOW_FINANCING)**: Net cash flow from financing activities.
24. **net_cash_flow_investing (NET_CASH_FLOW_INVESTING)**: Net cash flow from investing activities.
25. **net_cash_flow_operating (NET_CASH_FLOW_OPERATING)**: Net cash flow from operating activities.
26. **common_shares_outstanding (SHARES)**: Number of common shares outstanding.
27. **total_equity (EQUITY)**: The company's total equity.
28. **dividends_per_share (DIVIDENDS_PER_SHARE)**: Dividends paid per share.
29. **market_value (MARKET_VALUE)**: The company's market value.
30. **price **: The company's closing stock price.

### Derived Financial Metrics
31. **revenue_growth (REVENUE_GROWTH)**: Year-over-year revenue growth percentage.
32. **eps_growth (EPS_GROWTH)**: Year-over-year earnings per share growth.
33. **dividend_growth (DIVIDEND_GROWTH)**: Year-over-year growth in dividends per share.
34. **net_profit_margin (NET_PROFIT_MARGIN)**: Net income as a percentage of total revenue.
35. **operating_margin (OPERATING_MARGIN)**: Operating profit as a percentage of total revenue.
36. **gross_margin (GROSS_MARGIN)**: Gross profit as a percentage of total revenue.
37. **return_on_assets (ROA)**: Net income as a percentage of total assets.
38. **return_on_equity (ROE)**: Net income as a percentage of total equity.
39. **return_on_invested_capital (ROIC)**: Net income as a percentage of (total assets - total liabilities).
40. **free_cash_flow (FCF)**: Net cash flow from operations minus capital expenditures.
41. **free_cash_flow_margin (FCF_MARGIN)**: Free cash flow as a percentage of total revenue.
42. **debt_to_equity (D/E)**: (Current debt + Long-term debt) divided by total equity.
43. **debt_to_assets (D/A)**: (Current debt + Long-term debt) divided by total assets.
44. **price_to_earnings_ratio (P/E)**: Closing stock price divided by earnings per share.
45. **price_to_book_ratio (P/B)**: Market value divided by total equity.
46. **price_to_share_ratio (P/S)**: Market value divided by common shares outstanding.
47. **EV_to_EBITDA_ratio (EV/EBITDA)**: (Market value + total liabilities - cash) divided by EBITDA.
"""

# Function to interact with the agent and execute the query
def query_agent(user_input):
    query = HumanMessage(content=f"{column_description}\n\n{user_input}")
    full_response = ""
    for step in agent_executor.stream({"messages": [query]}, {"configurable": {"thread_id": "thread-001"}}, stream_mode="values"):
        if step["messages"] and isinstance(step["messages"][-1], AIMessage):
            chunk = step["messages"][-1].content
            full_response += chunk
    return full_response


if __name__ == "__main__":
    user_message = sys.argv[1]  
    response = query_agent(user_message)
    print(response) 
