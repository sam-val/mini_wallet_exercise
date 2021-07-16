from django.db import models
import uuid
from django.db.models.deletion import SET_NULL

from django.db.models.fields import BooleanField, DateTimeField, PositiveBigIntegerField, UUIDField
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# Create your models here.


class Customer(AbstractUser):
    username = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(null=True)

    def __str__(self) -> str:
        return str(self.username)

class CommonInfo(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class Wallet(CommonInfo):
    balance = PositiveBigIntegerField(default=0)
    status = BooleanField(default=False)
    owner = ForeignKey(Customer, related_name="wallet", on_delete=models.CASCADE)
    enabled_at = DateTimeField(null=True, blank=True)
    disabled_at = DateTimeField(null=True,blank=True)

    def __init__(self , *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._prev_status = self.status

    def save(self, *args, **kwargs):
        if not self._prev_status and self.status: ## false(disabled) => true(enabled)
            self.enabled_at = timezone.now()
        elif not self.status: ## if status is false when save()
            self.disabled_at = timezone.now()
        self._prev_status = self.status
        super().save(*args, **kwargs)

class Deposit(CommonInfo):
    amount = PositiveBigIntegerField()
    owner = ForeignKey(Customer, related_name="deposit", on_delete=models.CASCADE)
    reference = UUIDField(default=uuid.uuid4, unique=True)
    deposited_at = DateTimeField(default=timezone.now)

class Withdrawal(CommonInfo):
    amount = PositiveBigIntegerField()
    withdrawn_at = DateTimeField(default=timezone.now)
    reference = UUIDField(default=uuid.uuid4, unique=True)
    owner = ForeignKey(Customer, related_name="withdrawal", on_delete=models.CASCADE)