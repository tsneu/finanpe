import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Transacao


class QuestionModelTests(TestCase):
    def test_was_transaction_recently_with_future_buy(self):
        """
        was_transaction_recently() returns False for transactions whose data_compra
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_buy = Transacao(data_compra=time.date())
        self.assertIs(future_buy.was_buy_recently(), False)