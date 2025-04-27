import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 查询任务数据
data = [
    {"任务": "Q1", "gStore": 5.38, "MySQL": 7.00},
    {"任务": "Q", "gStore": 20.68, "MySQL": 35.66},
    {"任务": "Q4", "gStore": 5.16, "MySQL": 6.00},
    {"任务": "Q5", "gStore": 0.44, "MySQL": 1.98},
]

df = pd.DataFrame(data)
df_melt = df.melt(id_vars="任务", var_name="数据库", value_name="耗时(ms)")

# 设置图表样式
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
barplot = sns.barplot(data=df_melt, x="任务", y="耗时(ms)", hue="数据库", palette="Set2")

# 添加标签
for p in barplot.patches:
    barplot.annotate(f'{p.get_height():.2f}',
                     (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=9)

plt.title("gStore vs MySQL 查询耗时对比", fontsize=14)
plt.tight_layout()
plt.savefig("query_time_comparison.png", dpi=300, bbox_inches='tight')  # 添加bbox_inches防止标签被截断
plt.show()