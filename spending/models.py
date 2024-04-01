from django.db import models
from accounts.models import CustomUser
from django.core.validators import MinValueValidator

class Payment(models.Model):
    CATEGORY = (('食費', '食費'),
                ('日用品','日用品'),
                ('交通費', '交通費'),
                ('趣味・娯楽', '趣味・娯楽'),
                ('交際費', '交際費'),
                ('衣服・美容', '衣服・美容'),
                ('水道・光熱費','水道・光熱費'),
                ('家賃','家賃'),
                ('医療・健康','医療・健康'),
                ('通信費','通信費'),
                ('保険','保険'),
                ('その他','その他'),
                )
    KINDS = (('消費', '消費'),
            ('浪費', '浪費'),
            ('投資','投資'),)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='金額', validators=[
        MinValueValidator(0)])
    category = models.CharField(verbose_name='カテゴリ',max_length=50,choices=CATEGORY)
    memo = models.CharField(verbose_name='メモ',max_length=300)
    kinds = models.CharField(verbose_name='支出分類',max_length=20,choices=KINDS)
    date = models.DateField(verbose_name='日付')

    def __str__(self):
        return f'{self.user}{self.category}{self.amount}{self.memo}{self.date}'