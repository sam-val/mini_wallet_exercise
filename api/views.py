from django.shortcuts import render
from .serializers import DepositSerializer, ResponseFormatter, WalletSerializer, WithdrawalSerializer
from .models import Customer, Wallet, Withdrawal, Deposit
# from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.authtoken.models import Token

import uuid
# utils functions:


# Create your views here.

@api_view(['POST'])
def init(request):
    """
    generate a customer if not exist using param: customer_xid
    then generate a token & a wallet, return the token
    if customer exists, just return token
    """

    try:
        data = JSONParser().parse(request)
        customer_xid = data['customer_xid']
        # check if customer_xid is valid uuid:
        uuid.UUID(customer_xid)
    except KeyError:
        formatter = ResponseFormatter(status=False, data={'error':"customer_xid: Field is required"})
        return Response(formatter.formated_data, status=status.HTTP_400_BAD_REQUEST)

    except (ValueError, AttributeError):
        # not a valid uuid
        formatter = ResponseFormatter(status=False, data={'error':"customer_xid: not a valid uuid. Use this one: " + str(uuid.uuid4())})
        return Response(formatter.formated_data, status=status.HTTP_400_BAD_REQUEST)

    customer = Customer.objects.filter(username=customer_xid).first()
    if customer:
        token = customer.auth_token
    else:
        customer = Customer.objects.create(username=customer_xid)
        token = Token.objects.create(user=customer)
        # create a wallet/account:
        Wallet.objects.create(owner=customer)

    formatter = ResponseFormatter(status=True, data={'token': token.key})
    return Response(data=formatter.formated_data)


@api_view(['GET', 'PATCH', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def wallet(request):
    """
    Check if token is bad, only proceed if it's good. Then...

    If method == GET:
        Check status of the wallet of this user, only proceed if it's true/enabled
        Then give client the wallet info.

    Elif method == POST:
        Check status of the wallet of this user, only proceed if it's false/unenabled
        Then enable the status to true

    Elif method == PATCH:
        Then disable the status

    """

    # this is true if the token provided is good (it exists, etc)
    if request.user.is_authenticated:
        wallet = request.user.wallet.get()
        data = JSONParser().parse(request)
        if request.method == "POST":
            if not wallet.status:
                wallet.status = True
                wallet.save()
                serializer = WalletSerializer(instance=wallet, method='post')
                formatter = ResponseFormatter(
                    status=True, data=serializer.data)
                return Response(formatter.formated_data)
            else:
                formatter = ResponseFormatter(
                    status=False, data={'error': "Wallet is already enabled"})
                return Response(formatter.formated_data, status=status.HTTP_403_FORBIDDEN)

        elif request.method == "GET":
            if not wallet.status:
                serializer = ResponseFormatter(
                    status=False, data={"error": "Please enable your wallet first."})
                return Response(serializer.formated_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = WalletSerializer(instance=wallet, method='get')
                formatter = ResponseFormatter(
                    status=True, data=serializer.data)
                return Response(formatter.formated_data)
        elif request.method == "PATCH":
            is_disabled = data.get('is_disabled', None)
            if is_disabled is True:
                wallet.status = False
                wallet.save()
                serializer = WalletSerializer(instance=wallet, method='patch')
                formatter = ResponseFormatter(
                    status=True, data=serializer.data)
                return Response(formatter.formated_data)
            elif is_disabled == None:
                f = ResponseFormatter(status=False, data={'error': {'is_disabled': "This field is required"}})
                return Response(f.formated_data, status=status.HTTP_204_NO_CONTENT)
            else:
                f = ResponseFormatter(status=False, data={'error': {'is_disabled': "Value of non true has no effect at this endpoint"}})
                return Response(f.formated_data, status=status.HTTP_204_NO_CONTENT)

    else:
        serializer = ResponseFormatter(
            status=False, data={"error": "Unvalid Token"})
        return Response(serializer.formated_data, status=status.HTTP_400_BAD_REQUEST)


@ api_view(['POST'])
@permission_classes([IsAuthenticated])
@ authentication_classes([TokenAuthentication])
def deposits(request):
    """
    check if wallet is enabled
    check if amount if valid
    check if reference_id is valid, as well as if it's hasn't been in the database
    we can do these checks in the serializer

    """
    wallet = request.user.wallet.get()
    if not wallet.status:
        formatter = ResponseFormatter(
            status=False, data={"error": "Please enable your wallet first."})
        return Response(formatter.formated_data, status=status.HTTP_400_BAD_REQUEST)
    data = JSONParser().parse(request)
    data['deposited_by'] = request.user.username
    serializer = DepositSerializer(data=data, wallet=wallet)
    if serializer.is_valid():
        serializer.save()
        # actually update the money:
        try:
            wallet.balance += data['amount']
            wallet.save()
        except (Exception) as e:
            import sys
            print(e, file=sys.stderr)
            formatter = ResponseFormatter(
                status=False, data={"error": "Transaction unsuccessful."})
            return Response(formatter.formated_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        formatter = ResponseFormatter(status=True, data=serializer.data)
        return Response(formatter.formated_data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def withdrawals(request):
    """
    check if wallet is enabled.

    WithdrawalSerializer.is.valid() will :
        check if amount if valid (only positive, less than current balance)
        check if reference_id is valid, as well as if it's hasn't been in the database

    If okay, perform transaction.
    """

    wallet = request.user.wallet.get()
    if not wallet.status:
        formatter = ResponseFormatter(
            status=False, data={"error": "Please enable your wallet first."})
        return Response(formatter.formated_data, status=status.HTTP_400_BAD_REQUEST)
    data = JSONParser().parse(request)
    data['withdrawn_by'] = request.user.username

    serializer = WithdrawalSerializer(data=data, wallet=wallet)
    if serializer.is_valid():
        serializer.save()
        # actually subtract money from wallet:
        try:
            wallet.balance -= data['amount']
            wallet.save()
        except (Exception) as e:
            formatter = ResponseFormatter(
                status=False, data={"error": "Transaction unsuccessful."})
            return Response(formatter.formated_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        formatter = ResponseFormatter(status=True, data=serializer.data)
        return Response(formatter.formated_data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
