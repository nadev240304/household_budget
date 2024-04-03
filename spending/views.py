from django.shortcuts import render, redirect
from django.views.generic import ListView,CreateView,TemplateView, DeleteView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django_pandas.io import read_frame
from django.contrib import messages
import numpy as np
import pandas as pd

from .plugin_plotly import GraphGenerator
from .models import Payment
from .forms import SpendingCreateForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import SpendingSearchForm

# プロフィール
class ProfileView(TemplateView):
    template_name = 'profile.html'

# トップページ
class TitleView(TemplateView):
    template_name = 'spending_title.html'

# 支出一覧
@method_decorator(login_required, name='dispatch')
class IndexView(LoginRequiredMixin, ListView):
    template_name = 'index.html'
    paginate_by = 10
    context_object_name = 'orderby_records'
    model = Payment
    queryset = Payment.objects.all()  # デフォルトでは全ての支出レコードを取得

    def get_queryset(self):
        # ログインユーザーに関連するレコードのみをフィルタリング
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).order_by('-date','-id')
        self.form = form = SpendingSearchForm(self.request.GET or None)

        if form.is_valid(): # バリデーションチェック
            # form.cleaned_data：バリデーションをクリアしたデータのみをディクショナリに格納
            year = form.cleaned_data.get('year') # 'year'キーで値を取り出す

            # 選択なし：文字列'0'が入るため除外
            if year and year != '0':
                queryset = queryset.filter(date__year=year)

            # 選択なし：文字列'0'が入るため除外
            month = form.cleaned_data.get('month')
            if month and month != '0':
                queryset = queryset.filter(date__month=month)
            
            kinds = form.cleaned_data.get('kinds')
            if kinds:
                queryset = queryset.filter(kinds=kinds)
        return queryset
    
    def get_context_data(self, **kwargs): # オーバーライド
        context = super().get_context_data(**kwargs)  # 親クラスの get_context_dataメソッドを実行
        context['search_form'] = self.form  # search_form変数をcontextに追加

        return context # テンプレートをcontextに渡す{{ search_form }}で使用

    def get(self, request, **kwargs):
        if request.GET:
            request.session['query'] = request.GET
        else:
            request.GET = request.GET.copy()
            if 'query' in request.session.keys():
                for key in request.session['query'].keys():
                    request.GET[key] = request.session['query'][key]

        return super().get(request, **kwargs)

# 支出登録
@method_decorator(login_required, name='dispatch')
class SpendingCreate(CreateView):
    form_class = SpendingCreateForm
    template_name = 'create.html'
    model = Payment
    success_url = reverse_lazy('spending:index')

    def form_valid(self, form):
        spendingdata = form.save(commit=False)
        spendingdata.user = self.request.user
        spendingdata.save()
        messages.success(self.request, "支出を登録しました！", extra_tags='info')
        return super().form_valid(form)

# 支出削除
@method_decorator(login_required, name='dispatch')
class SpendingDelete(DeleteView):
    template_name = 'delete.html'
    model = Payment
    success_url = reverse_lazy('spending:index')

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, "削除が完了しました！", extra_tags='info')
        return super().form_valid(form)

# 支出更新処理
@method_decorator(login_required, name='dispatch')
class SpendingUpdate(UpdateView):
    template_name = 'edit.html'
    model = Payment
    form_class = SpendingCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy('spending:index')

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "編集が完了しました！", extra_tags='info')
        return redirect(self.get_success_url())

# 月間支出
@method_decorator(login_required, name='dispatch')
class MonthDashboard(TemplateView):
    template_name = 'month_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # これから表示する年月
        year = int(self.kwargs.get('year'))
        month = int(self.kwargs.get('month'))
        context['year_month'] = f'{year}年{month}月'

        # 前月と次月をコンテキストに入れて渡す
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1

        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
        context['prev_year'] = prev_year
        context['prev_month'] = prev_month
        context['next_year'] = next_year
        context['next_month'] = next_month

        # paymentモデルをdfにする
        queryset = Payment.objects.filter(date__year=year)
        queryset = queryset.filter(date__month=month)
        queryset = queryset.filter(user=self.request.user).order_by('-date')

        # クエリセットが何もない時はcontextを返す
        if not queryset:
            return context

        df = read_frame(queryset,
                        fieldnames=['date', 'amount', 'category', 'kinds'])

        # グラフ作成クラスをインスタンス化
        gen = GraphGenerator()

        # pieチャートの素材を作成
        df_pie = pd.pivot_table(df, index='category', values='amount', aggfunc=np.sum)
        pie_labels = list(df_pie.index.values)
        pie_values = [val[0] for val in df_pie.values]
        plot_pie = gen.month_pie(labels=pie_labels, values=pie_values)
        context['plot_pie'] = plot_pie

        # 支払分類グラフ
        df_pie_kinds = pd.pivot_table(df, index='kinds', values='amount', aggfunc=np.sum)
        pie_kinds_labels = list(df_pie_kinds.index.values)
        pie_kinds_values = [val[0] for val in df_pie_kinds.values]
        plot_pie_kinds = gen.month_kinds_pie(labels=pie_kinds_labels, values=pie_kinds_values)
        context['plot_pie_kinds'] = plot_pie_kinds

        # テーブルでのカテゴリと金額の表示用。
        # {カテゴリ:金額,カテゴリ:金額…}の辞書を作る
        context['table_set'] = df_pie.to_dict()['amount']

        # totalの数字を計算して渡す
        context['total_payment'] = df['amount'].sum()

        return context