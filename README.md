自動生成銷售報告 (Auto Generate Sales Report using LangChain)
這是一個使用 Python + Pandas + LangChain 分析銷售數據並生成銷售報告的專案。本專案讀取 Sales.csv，對數據進行整理、計算，並透過 OpenAI LLM 自動生成詳細的銷售分析報告。

1️⃣ 功能特色
✅ 讀取並清理銷售數據 (Sales.csv)
✅ 分析 各州、各產品、各月份的銷售趨勢
✅ 計算各產品在不同地區的銷售占比
✅ 透過 OpenAI LLM 生成完整的銷售報告
✅ 自動輸出 TXT 文件 (final_report.txt)

2️⃣PromptTemplate（提示模板）
使用了 PromptTemplate 來定義 AI 要生成的報告內容，包括 關鍵見解、趨勢分析、產品表現、優化建議 等：

3️⃣ 使用 PromptTemplate + LLM 生成報告
你使用了 |（管道運算符）來組合不同的 LangChain 組件：
prompt → PromptTemplate，定義要讓 AI 生成的內容
llm → OpenAI()，調用 OpenAI GPT 來生成文本
StrOutputParser() → 解析 AI 的回應，轉換為純文本格式
這樣 LangChain 會自動處理提示詞、傳遞數據給 LLM，然後解析回應。


想法:如果有制式的報表，把 step 2的分析公式以及prompt寫好，就可以每run 一次都跑出自己要的簡約文字報告了

