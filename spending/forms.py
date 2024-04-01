from django import forms
from .models import Payment
from django.utils import timezone

class SpendingCreateForm(forms.ModelForm):
    kinds = forms.ChoiceField(choices=[('消費', '消費'), ('浪費', '浪費'), ('投資', '投資')], widget=forms.RadioSelect,label='支払分類')
    class Meta:
        model = Payment
        fields = ['amount', 'category', 'memo', 'kinds', 'date']

class SpendingSearchForm(forms.Form):
    # 年の選択肢を動的に作る
    start_year = 2024  # 家計簿の登録を始めた年
    end_year = timezone.now().year + 1  # 現在の年＋１年
    years = [(year, f'{year}年') for year in reversed(range(start_year, end_year + 1))]
    years.insert(0, (0, ''))  # 空白の選択を追加
    YEAR_CHOICES = tuple(years)

    # 月の選択肢を動的に作る
    months = [(month, f'{month}月') for month in range(1, 13)]
    months.insert(0, (0, ''))
    MONTH_CHOICES = tuple(months)

    # 年の選択
    year = forms.ChoiceField(
        required=False,
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form'})
    )

    # 月の選択
    month = forms.ChoiceField(
        required=False,
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form'})
    )

    kinds = forms.ChoiceField(
        required=False,
        choices=[('', ''),('消費', '消費'), ('浪費', '浪費'), ('投資', '投資')],
        widget=forms.Select(attrs={'class': 'form'}),
    )