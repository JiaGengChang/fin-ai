import os
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import Tool, StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib
from pydantic import BaseModel
from typing import List, Optional

# Load environment variables
assert load_dotenv('.env') or load_dotenv('../.env')
openai_api_key = os.getenv("OPENAI_API_KEY")
model = init_chat_model(os.getenv("OPENAI_MODEL_NAME","gpt-4o-mini"), model_provider="openai", max_tokens=2000, temperature=0.3)
memory = MemorySaver()
matplotlib.use('Agg')

try:
    db_uri = f'mysql+mysqlconnector://{os.getenv("MYSQL_USER",'root')}:{os.getenv("MYSQL_PASSWORD",'password')}@{os.getenv("MYSQL_HOST",'localhost')}:{os.getenv("MYSQL_PORT",3306)}/financial_db'
    db = SQLDatabase.from_uri(db_uri)
    query_sql_tool = QuerySQLDatabaseTool(db=db)
except Exception as e:
    print(f'Could not connect to MySQL DB. Check DB_URI or make sure server is running. Error: {e}')
    exit(1)

repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with print(...).",
    func=PythonREPL().run,
)

class PlotInput(BaseModel):
    x: List[int|str]
    y: List[float]
    graph_folder: str
    filename: str
    title: Optional[str] = "Plot"
    xlabel: Optional[str] = "X"
    ylabel: Optional[str] = "Y"

class MultiPlotInput(BaseModel):
    x: List[int|str]
    y: List[List[float]]
    labels: List[str]
    graph_folder: str
    filename: str
    title: Optional[str] = "Plot"
    xlabel: Optional[str] = "X"
    ylabel: Optional[str] = "Y"

def generate_line_plot(x, y, graph_folder, filename, title="Line Plot", xlabel="X", ylabel="Y"):
    dir = os.path.dirname(graph_folder)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    plt.figure()
    plt.plot(x, y, marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    path = os.path.join(graph_folder, filename)
    plt.savefig(path)
    plt.close()

def generate_multiline_plot(x, y, graph_folder, filename, title="Multiline Plot", xlabel="X", ylabel="Y", labels=None):
    dir = os.path.dirname(graph_folder)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    plt.figure()
    for i, y_values in enumerate(y):
        plt.plot(x, y_values, marker="o", label=labels[i])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)

    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    path = os.path.join(graph_folder, filename)
    plt.savefig(path)
    plt.close()

def generate_bar_plot(x, y, graph_folder, filename, title="Bar Plot", xlabel="X", ylabel="Y"):
    dir = os.path.dirname(graph_folder)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    plt.figure()
    plt.bar(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45,ha='right')
    plt.grid(axis='y')

    plt.tight_layout()

    path = os.path.join(graph_folder, filename)
    plt.savefig(path)
    plt.close()

def generate_pie_chart(x, y, graph_folder, filename, title="Pie Chart"):
    dir = os.path.dirname(graph_folder)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    plt.figure(figsize=(8, 5))
    
    plt.pie(y, labels=x, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.tight_layout()

    path = os.path.join(graph_folder, filename)
    plt.savefig(path)
    plt.close()

def generate_line_plot_wrapper(inputs: PlotInput) -> str:
    generate_line_plot(inputs.x, inputs.y, inputs.graph_folder, inputs.filename, inputs.title, inputs.xlabel, inputs.ylabel)
    return f"Graph generated: {inputs.graph_folder}/{inputs.filename}"

def generate_multiline_plot_wrapper(inputs: MultiPlotInput) -> str:
    generate_multiline_plot(inputs.x, inputs.y, inputs.graph_folder, inputs.filename, inputs.title, inputs.xlabel, inputs.ylabel, inputs.labels)
    return f"Graph generated: {inputs.graph_folder}/{inputs.filename}"

def generate_bar_plot_wrapper(inputs: PlotInput) -> str:
    generate_bar_plot(inputs.x, inputs.y, inputs.graph_folder, inputs.filename, inputs.title, inputs.xlabel, inputs.ylabel)
    return f"Graph generated: {inputs.graph_folder}/{inputs.filename}"

def generate_pie_chart_wrapper(inputs: PlotInput) -> str:
    generate_pie_chart(inputs.x, inputs.y, inputs.graph_folder, inputs.filename, inputs.title)
    return f"Graph generated: {inputs.graph_folder}/{inputs.filename}"

graph_line_plot_tool = StructuredTool.from_function(
    func=generate_line_plot_wrapper,
    input_schema=PlotInput,
    description=(
        "Use this tool to generate line plots. "
        "Required keys: 'x' (list of x values), 'y' (list of y values), 'graph_folder' (folder to save graph in)."
        "Optional: 'filename', 'title (title of the figure)', 'xlabel (name of horizontal axis)', 'ylabel (name of vertical axis)'."
    )
)

graph_multiline_plot_tool = StructuredTool.from_function(
    func=generate_multiline_plot_wrapper,
    input_schema=MultiPlotInput,
    description=(
        "Use this tool to generate line plots for M multiple datasets. "
        "Required keys: 'x' (list of x-values), 'y' (list of M lists of y-values), 's' (list of M labels), 'graph_folder' (folder to save graph in)."
        "Optional: 'filename', 'title (title of the figure)', 'xlabel (name of horizontal axis)', 'ylabel (name of vertical axis)'."
    )
)

graph_bar_plot_tool = StructuredTool.from_function(
    func=generate_bar_plot_wrapper,
    input_schema=PlotInput,
    description=(
        "Use this tool to generate bar plots."
        "Required keys: 'x' (list of x values), 'y' (list of y values), 'graph_folder' (folder to save graph in)."
        "Optional: 'filename', 'title (title of the figure)', 'xlabel (name of horizontal axis)', 'ylabel (name of vertical axis)'."
    )
)

graph_pie_chart_tool = StructuredTool.from_function(
    func=generate_pie_chart_wrapper,
    input_schema=PlotInput,
    description=(
        "Use this tool to generate pie charts."
        "Required keys: 'x' (list of labels), 'y' (list of values), 'graph_folder' (folder to save graph in)."
        "Optional: 'filename', 'title (title of the figure)'."
    )
)

tools = [repl_tool, query_sql_tool, graph_line_plot_tool, graph_multiline_plot_tool, graph_bar_plot_tool, graph_pie_chart_tool]

agent_executor = create_react_agent(model, tools, checkpointer=memory)

db_description = """
The finanal_db database has one main table: `company_data`, with the following structure:

### Company Metadata and Financial Data
1. company_id: Unique identifier for the company.
2. ticker: The stock ticker symbol of the company.
3. company_name: Full name of the company.
4. country: The country where the company is based.
5. industry_code: Numeric code representing the company's industry classification.
6. year: The fiscal year of the financial data.

### Base Financial Data
7. current_assets: The company's current assets (in millions USD).
8. total_assets: The company's total assets (in millions USD).
9. cash: The company's cash on hand (in millions USD).
10. current_debt: The company's current debt (in millions USD).
11. long_term_debt: The company's long-term debt (in millions USD).
12. invested_capital: The company's total invested capital (in millions USD).
13. total_liabilities: The company's total liabilities (in millions USD).
14. cost_of_goods_sold: The cost of goods sold (in millions USD).
15. ebit: Earnings before interest and taxes (in millions USD).
16. ebitda: Earnings before interest, taxes, depreciation, and amortization (in millions USD).
17. eps: Earnings per share (in USD).
18. net_income: The company's net income (in millions USD).
19. total_revenue: The company's total revenue (in millions USD).
20. income_taxes: Income taxes (in millions USD).
21. interest_expense: The company's interest expenses (in millions USD).
22. capital_expenditures: The company's capital expenditures (in millions USD).
23. net_cash_flow_financing: Net cash flow from financing activities (in millions USD).
24. net_cash_flow_investing: Net cash flow from investing activities (in millions USD).
25. net_cash_flow_operating: Net cash flow from operating activities (in millions USD).
26. common_shares_outstanding: Number of common shares outstanding.
27. total_equity: total shareholder's equity.
28. dividends_per_share: Dividends paid per share (in USD).
29. market_value: The company's market capitalization value (in millions USD).
30. price: The company's closing stock price (in USD).
31. gross_profit: The company's gross profit (in millions USD).

### Derived Financial Metrics
32. revenue_growth: Year-over-year revenue growth percentage.
33. eps_growth: Year-over-year earnings per share growth.
34. dividend_growth: Year-over-year growth in dividends per share as a percentage.
35. net_profit_margin: Net income as a percentage of total revenue.
36. operating_margin: Operating profit as a percentage of total revenue.
37. gross_margin: Gross profit as a percentage of total revenue.
38. return_on_assets: (ROA) Net income as a percentage of total assets.
39. return_on_equity: (ROE) Net income as a percentage of total equity.
40. return_on_invested_capital: (ROIC) Net income as a percentage of (total assets - total liabilities).
41. free_cash_flow: (FCF) Net cash flow from operations minus capital expenditures (in millions USD).
42. free_cash_flow_margin: (FCF margin) Free cash flow as a percentage of total revenue.
43. debt_to_equity: (D/E) (Current debt + Long-term debt) divided by total equity.
44. debt_to_assets: (D/A) (Current debt + Long-term debt) divided by total assets.
45. price_to_earnings_ratio: (P/E) Closing stock price divided by earnings per share.
46. price_to_book_ratio: (P/B) Market value divided by total equity.
47. price_to_share_ratio: (P/S) Market value divided by common shares outstanding.
48. EV_to_EBITDA_ratio: (EV/EBITDA) (Market value + total liabilities - cash) divided by EBITDA.

Use the `ticker` column to identify companies when a company name or stock symbol is mentioned.
"""

system_message = SystemMessage(content=\
"""
You are a financial analysis agent living in 2025, designed to interact with a SQL database containing company financial data.
You will answer questions with as few words as possible, providing concise information and no-nonsense communication.

If the question is related to the financial data of companies (for example, asking about revenue, earnings, or financial ratios), 
you will query the 'company_data' table in the database, which contains data up to the fiscal year 2024. 
If the year is not specified in the query, you will assume the most recent year available in the database (2024).
If the question is general in nature (such as asking for the capital of a country or historical events), 
you will provide an answer using your internal knowledge base, drawing from common knowledge and general sources.

{db_description}

Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can then order the results by a relevant column to return the most interesting examples in the database.
Only ask for the relevant columns given the question, never query for all the columns from a specific table.
If the user repeatedly asks for ALL information in the database, you can suggest the list of available columns.
Do not allow the user to query for all columns in the database as this is not useful and will result in a large amount of data.

You MUST double check your query before executing it. 
If you get an error while executing a query, rewrite the query and try again.
DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If the query result is empty, return a message indicating that no data was found for the query. Do NOT return hypothetical examples.

If the query result has fewer than 3 data points, bypass graph creation and return a text-based answer.

If the query result has 3 or more data points, follow these instructions below:

If the query results include array-like data (e.g., multiple years of data for a company, or multiple companies in a specific year or industry code),
use the following tools available to generate a relevant chart. 

1. `graph_line_plot_tool`: Use this if the question is about a trend over time for one company.
2. `graph_multiline_plot_tool`: Use this if the question is about comparing multiple time series.
3. `graph_bar_plot_tool`: Use this if the question is about different companies in a specific year.
4. `graph_pie_chart_tool`: Use this if the question is about the breakdown of a quantity into different aspects.

If the query result has 3 to 10 data points, return a text-based answer in addition to the graph. 
If the query result has more than 10 data points, return only the graph and do NOT return the raw values in text.

""".format(
    dialect="MySQL",
    top_k=5,
    db_description=db_description
))

def query_agent(user_input: str):
    user_message = HumanMessage(content=user_input)
    config = {"configurable": {"thread_id": "thread-001"}}
    full_response = ""

    for step in agent_executor.stream({"messages": [system_message, user_message]}, config, stream_mode="values"):
        if step["messages"]:
            step["messages"][-1].pretty_print()
        if step["messages"] and isinstance(step["messages"][-1], AIMessage):
            chunk = step["messages"][-1].content
            full_response += chunk
    return full_response
