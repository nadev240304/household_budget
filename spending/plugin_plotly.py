import plotly.graph_objects as go

    # 支出金額グラフ
class GraphGenerator:
    def month_pie(self, labels, values):
        colors = ['Lavender','LightCyan','LightSeaGreen','LightSkyBlue',
                  'LightSalmon','LightGoldenRodYellow','LightGreen','LightPink',
                  'LightCoral','LightBlue','LightGray','SlateGray']
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=labels,values=values, marker=dict(colors=colors)))
        # fig.update_layout(title='カテゴリ別')
        fig.update_layout(title=dict(text='カテゴリ別支出',
                            font=dict(family='Times New Roman', size=30, color='Gray'),
                            x=0.5,y=0.9))
        return fig.to_html()

    # 支払分類グラフ
    def month_kinds_pie(self, labels, values):
        colors = ['SandyBrown', 'PaleTurquoise', 'Wheat']  # グラフの色のリスト
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=labels, values=values, hole=0.3, marker=dict(colors=colors)))
        fig.update_layout(title=dict(text='支出分類',
                            font=dict(family='Times New Roman', size=30, color='Gray'),x=0.5,y=0.9))
        return fig.to_html()