#pip install pandas
#pip install langchain
#pip install langchain-core                           
#pip install langchain-openai 
#pip install numpy  
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAI
import os 
import openai
#設置API KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Step 1: 載入數據
data_path = "C:/Users/USER/Desktop/AI FREE TEAM/Lang Chain(chat with data)/1 auto generate report from csv/Sales.csv"
df = pd.read_csv(data_path)
df.head(5)

# Step 2: 數據分析
#嘗試刪除2015，2016以外的年份
# 找出需要刪除的索引
indices_to_drop = df[df['Year'].isin([2011,2012,2013,2014])].index
# 使用 drop 方法刪除
df = df.drop(indices_to_drop)
df.head(5)
# 1.按 Region 和 State 分組，計算總銷售額
## 將 Date 字段轉換為日期類型，其實這裡也可以直接用Year欄去做，但想試試看從完整年月日切分出來
df['Date'] = pd.to_datetime(df['Date'])
# 添加月份字段
df['Year_c'] = df['Date'].dt.to_period('Y')  # 按年
summary_by_state = df.groupby(['Year_c','Country', 'State'])['Revenue'].sum().reset_index()
print(summary_by_state)

# 2.按月份，計算銷售總和
## 將 Date 字段轉換為日期類型
#df['Date'] = pd.to_datetime(df['Date'])
# 添加月份字段
df['Month'] = df['Date'].dt.to_period('M')  # 按月
monthly_sales= df.groupby(['Year_c','Month'])['Revenue'].sum().reset_index()
print(monthly_sales)

#3.sub_category 子分類 product具體產品
#要修改掉L、M、S，產品名稱還分size太細了，我希望是一個產品就是一個
df['Product'] = df['Product'].str.split(',').str[0] #透過 split() 函數移除 , 之後的部分，僅保留產品名稱。
print(df['Product'].unique()) # 檢查處理後的數據
summary_by_product=df.groupby(['Year_c','Product'])['Revenue'].sum().reset_index()
print(summary_by_product)

#4.計算某一地區商品類型的占比，但這邊因為要對齊才能相除，所以寫法會跟剛剛不一樣
#計算各地總銷售額，用剛剛的1.分割到product， 'Year_c','Country', 'State','Product'
summary_by_product_2 = df.groupby(['Year_c','Product'])['Revenue'].sum()
print(summary_by_product_2)
#要用summary_by_state但是這次加總到'Year_c','Country', 'State'而不分到product
summary_revenue_for_each_state=summary_by_product_2.groupby(['Year_c']).sum()
print(summary_revenue_for_each_state)
product_percentage_of_state = (summary_by_product_2/summary_revenue_for_each_state).reset_index()
print(product_percentage_of_state)

#把資料排序後再取前20行
# 1.
final_summary_by_state=summary_by_state.sort_values(by='Revenue', ascending=False).head(20)
print(final_summary_by_state)
#2.
final_monthly_sales= monthly_sales.sort_values(by='Revenue', ascending=False).head(20)
print(final_monthly_sales)
#3.
final_summary_by_product= summary_by_product.sort_values(by='Revenue', ascending=False).head(20)
print(final_summary_by_product)
#4.
final_product_percentage_of_state=product_percentage_of_state.sort_values(by='Revenue', ascending=False).head(20)
print(final_product_percentage_of_state)
#

# 分析結果作為輸入
analysis_summary = f"""
1.Total Sales by State:
{final_summary_by_state.to_string(index=False)}

2. Monthly sales trend:
{final_monthly_sales.to_string(index=False)}

3. calculate each product's revenue:
{final_summary_by_product.to_string(index=False)}

4. calculate product_percentage_each_year:
{final_product_percentage_of_state.to_string(index=False)}
"""

# Step 3: 利用 LLM 生成報表
llm = OpenAI()
# 設置模板
template = """
You are a professional data analyst. Based on the following analysis results, generate a concise and insightful sales report:
Generate a sales report based on the data:
{analysis_summary}

Include the following sections:
1. Key insights from the data. Provide detailed insights into the sales figures, breaking down the information by region, product, and time period.
2. Observed trends over time. Identify any notable patterns, seasonal trends, or changes in sales performance over months or years.
3. A deep dive into each product's performance, including factors that may have contributed to high or low sales.
4. Specific recommendations for improving performance in underperforming regions, products, or months. Suggest actionable strategies for boosting sales, such as targeted marketing, promotions, or product improvements.
5. Provide a comparison of the current year's performance with the previous years, and analyze any significant changes or shifts in the sales landscape.
6. Offer a forecast or predictions for the next quarter or year, based on the current data trends.

Please make sure the report is in-depth, well-organized, and covers every angle of the sales analysis. Aim for a detailed, comprehensive report, and use at least 2000 words. 

Ensure that your report is clear, concise, and professional, and contains no unnecessary repetition. Your goal is to provide actionable insights to help the business grow.

"""
prompt = PromptTemplate(input_variables=["analysis_summary"], template=template)


# 使用新的鏈接語法 {使用 LangChain 生成報表 chain = LLMChain(llm=llm, prompt=prompt)已經被棄用了}
# prompt | llm | StrOutputParser() 是新的寫法，這利用了 |（管道運算符）來將提示模板、LLM 和輸出解析器串聯起來，這樣可以更直觀地處理不同的步驟。
# 這樣的設計讓流程更為簡潔，您不再需要顯式地創建一個 LLMChain 對象，而是直接鏈接不同的組件。
chain = prompt | llm | StrOutputParser()
report = chain.invoke({"analysis_summary": analysis_summary})#使用 invoke() 方法來執行流程，並傳遞必要的參數。
print(report)

chunks = [analysis_summary[i:i+1000] for i in range(0, len(analysis_summary), 1000)]
for chunk in chunks:
    report = chain.invoke({"analysis_summary": chunk})
    print(report)

# 合併所有段的報告
full_report = []
for chunk in chunks:
    report = chain.invoke({"analysis_summary": chunk})
    full_report.append(report)

# 合併為完整報告
final_report = "\n\n".join(full_report)
print(final_report)
# 將 final_report 導出為 TXT 文件
with open("final_report.txt", "w", encoding="utf-8") as file:
    file.write(final_report)
print("Final report exported as final_report.txt")





