import os
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import Tool, StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib
from pydantic import BaseModel
from typing import List, Optional

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
model = init_chat_model("gpt-4o-mini", model_provider="openai", max_tokens=2000, temperature=0.3)
memory = MemorySaver()
matplotlib.use('Agg')

db = SQLDatabase.from_uri("mysql+mysqlconnector://root:t0220975b@localhost:3306/financial_db")
query_sql_tool = QuerySQLDatabaseTool(db=db)

repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with print(...).",
    func=PythonREPL().run,
)

class PlotInput(BaseModel):
    x: List[float]
    y: List[float]
    filename: Optional[str] = "graph.png"
    title: Optional[str] = "Line Plot"
    xlabel: Optional[str] = "X"
    ylabel: Optional[str] = "Y"

def generate_line_plot(x, y, filename="graph.png", title="Line Plot", xlabel="X", ylabel="Y"):
    plt.figure()
    plt.plot(x, y, marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    graph_folder = os.path.join(backend_dir, 'graph')
    os.makedirs(graph_folder, exist_ok=True)

    path = os.path.join(graph_folder, filename)
    plt.savefig(path)
    plt.close()

def generate_line_plot_wrapper(inputs: PlotInput) -> str:
    generate_line_plot(inputs.x, inputs.y, inputs.filename, inputs.title, inputs.xlabel, inputs.ylabel)
    return f"Graph generated: {inputs.filename}"

graph_plot_tool = StructuredTool.from_function(
    func=generate_line_plot_wrapper,
    input_schema=PlotInput,
    description=(
        "Use this tool to generate line plots. Required keys: "
        "'x' (list of x values), 'y' (list of y values). Optional: "
        "'filename', 'title', 'xlabel', 'ylabel'."
    )
)

tools = [query_sql_tool, graph_plot_tool, repl_tool]

agent_executor = create_react_agent(model, tools, checkpointer=memory)

column_description = """
The company_data table in the financial_db MySQL database contains the following columns:

### Company Metadata and Financial Data
1. company_id: Unique identifier for the company.
2. ticker: The stock ticker symbol of the company, use this to identify the company.
3. company_name: Full name of the company.
4. country: The country where the company is based.
5. industry_code: Numeric code representing the company's industry classification.
6. year: The fiscal year of the financial data.

### Base Financial Data
7. current_assets: The company's current assets.
8. total_assets: The company's total assets.
9. cash: The company's cash on hand.
10. current_debt: The company's current debt.
11. long_term_debt: The company's long-term debt.
12. invested_capital: The company's total invested capital.
13. total_liabilities: The company's total liabilities.
14. cost_of_goods_sold: The cost of goods sold.
15. ebit: Earnings before interest and taxes.
16. ebitda: Earnings before interest, taxes, depreciation, and amortization.
17. eps: Earnings per share.
18. net_income: The company's net income.
19. total_revenue: The company's total revenue.
20. income_taxes: Income taxes.
21. interest_expense: The company's interest expenses.
22. capital_expenditures: The company's capital expenditures.
23. net_cash_flow_financing: Net cash flow from financing activities.
24. net_cash_flow_investing: Net cash flow from investing activities.
25. net_cash_flow_operating: Net cash flow from operating activities.
26. common_shares_outstanding: Number of common shares outstanding.
27. total_equity: The company's total equity.
28. dividends_per_share: Dividends paid per share.
29. market_value: The company's market capitalization value.
30. price: The company's closing stock price.

### Derived Financial Metrics
31. revenue_growth: Year-over-year revenue growth percentage.
32. eps_growth: Year-over-year earnings per share growth.
33. dividend_growth: Year-over-year growth in dividends per share.
34. net_profit_margin: Net income as a percentage of total revenue.
35. operating_margin: Operating profit as a percentage of total revenue.
36. gross_margin: Gross profit as a percentage of total revenue.
37. return_on_assets(ROA): Net income as a percentage of total assets.
38. return_on_equity(ROE): Net income as a percentage of total equity.
39. return_on_invested_capital(ROIC): Net income as a percentage of (total assets - total liabilities).
40. free_cash_flow(FCF): Net cash flow from operations minus capital expenditures.
41. free_cash_flow_margin(FCF margin): Free cash flow as a percentage of total revenue.
42. debt_to_equity(D/E): (Current debt + Long-term debt) divided by total equity.
43. debt_to_assets(D/A) : (Current debt + Long-term debt) divided by total assets.
44. price_to_earnings_ratio(P/E) : Closing stock price divided by earnings per share.
45. price_to_book_ratio(P/B) : Market value divided by total equity.
46. price_to_share_ratio(P/S) : Market value divided by common shares outstanding.
47. EV_to_EBITDA_ratio(EV/EBITDA): (Market value + total liabilities - cash) divided by EBITDA.
"""

system_instruction = """
You are a financial data analyst assistant.

Your primary task is to analyze user questions using SQL queries and, where appropriate, Python code.

If the question involves trends, time-based comparisons, or visual insights (e.g., revenue over multiple years), generate and save graph using graph_plot_tool.

In your response, always:
1. Describe the analysis result clearly in plain English.
2. If a graph was generated, include the line: "Graph generated: graph/filename.png"
3. Return only the final response text — do not include any raw code, logs, or intermediate Python output.
"""

def query_agent(user_input: str):
    query = HumanMessage(content=f"{column_description}\n\n{user_input}")
    config = {"configurable": {"thread_id": "thread-001"}}
    full_response = ""

    for step in agent_executor.stream({"messages": [query]}, config, stream_mode="values"):
        if step["messages"]:
            step["messages"][-1].pretty_print()
        if step["messages"] and isinstance(step["messages"][-1], AIMessage):
            chunk = step["messages"][-1].content
            full_response += chunk
    return full_response
