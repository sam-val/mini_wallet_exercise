from uuid import uuid4
import uuid
from django.db.models.fields import BooleanField
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from .models import CommonInfo, Customer, Wallet, Withdrawal, Deposit


class ResponseFormatter:
    """
    Another wrapper/formatter
    """

    def __init__(self, status=False, data={}):
        self.formated_data = {}
        self.formated_data['status'] = "success" if status else "failed"
        self.formated_data['data'] = data


class CommonInfo(serializers.ModelSerializer):
    class Meta:
        model = CommonInfo
        fields = ['id']
        abstract = True

    def wrap_serializer(self, ret):
        output = {}
        output[f"{self.Meta.model.__name__.lower()}"] = ret
        return output


class WalletSerializer(CommonInfo):
    """

    this is only for reading
    you have to pass in a method keyword argument: "PATCH", "POST" or "GET"
    Example: WalletSerializer(method='get')

    """
    owned_by = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source='owner')

    class Meta:
        model = Wallet
        fields = ['id', 'status', 'owned_by',
                  'disabled_at', 'enabled_at', 'balance']

    def __init__(self, *args, **kwargs):
        self.method = kwargs.pop('method')
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if self.method.lower() in ['post', 'get']:
            ret.pop('disabled_at')
            ret['enabled_at'] = instance.enabled_at.replace(microsecond=0)
        elif self.method.lower() in ['patch']:
            ret.pop('enabled_at')
            ret['disabled_at'] = instance.disabled_at.replace(microsecond=0)

        ret['status'] = 'enabled' if ret['status'] else 'disabled'

        return self.wrap_serializer(ret)


class DepositSerializer(CommonInfo):
    reference_id = serializers.UUIDField(source='reference')

    deposited_by = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source='owner')

    def __init__(self, *args, **kwargs):
        self.wallet = kwargs.pop('wallet')
        self.fields['reference_id'].error_messages[
            'invalid'] = f"Must be a valid UUID. Try this: {str(uuid.uuid4())}"
        super().__init__(*args, **kwargs)

    class Meta:
        model = Deposit
        fields = ['id', 'deposited_by',
                  'deposited_at', 'amount', 'reference_id']

    def create(self, validate_data):
        return Deposit.objects.create(**validate_data)

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Deposit amount can't be negative")

        return value

    def validate_reference_id(self, value):

        if Deposit.objects.filter(reference=value).exists():
            raise serializers.ValidationError(
                "reference_id should be unique for every deposit.")

        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['deposited_at'] = instance.deposited_at.replace(microsecond=0)
        return self.wrap_serializer(ret)


class WithdrawalSerializer(CommonInfo):
    reference_id = serializers.UUIDField(source='reference')
    withdrawn_by = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source='owner')

    class Meta:
        model = Withdrawal
        fields = ['id', 'withdrawn_by',
                  'withdrawn_at', 'amount', 'reference_id']

    def __init__(self, *args, **kwargs):
        self.wallet = kwargs.pop('wallet')
        self.fields['reference_id'].error_messages[
            'invalid'] = f"Must be a valid UUID. Try this: {str(uuid.uuid4())}"
        super().__init__(*args, **kwargs)

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Withdrawing amount can't be negative")

        if value > self.wallet.balance:
            raise serializers.ValidationError(
                "Can't withdraw more than current balance")

        return value

    def validate_reference_id(self, value):

        if Withdrawal.objects.filter(reference=value).exists():
            raise serializers.ValidationError(
                "reference_id should be unique for every withdrawal. Try this: " + str(uuid.uuid4()))

        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['withdrawn_at'] = instance.withdrawn_at.replace(microsecond=0)
        return self.wrap_serializer(ret)
