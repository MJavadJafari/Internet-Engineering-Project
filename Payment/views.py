import logging

from azbankgateways import bankfactories
from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways.models import CurrencyEnum, BankType
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from MyUser.models import MyUser
from .models import Transaction
from azbankgateways import bankfactories, models as bank_models, default_settings as settings

from django.conf import settings as django_settings

from MyUser.permissions import OwnProfilePermission

logger = logging.getLogger(__name__)


class GoToGatewayView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        OwnProfilePermission
    ]

    def post(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "GoToGatewayView.post")
        duration = request.data.get('duration', None)
        if duration is None:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "GoToGatewayView.post: duration is None, response = 404")
            return Response(status=HTTP_400_BAD_REQUEST)
        duration = int(duration)

        if duration is None or duration not in Transaction.VIP_OPTIONS:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "GoToGatewayView.post: duration is None or not in Transaction.VIP_OPTIONS, response = 404")
            return Response(status=HTTP_400_BAD_REQUEST)

        amount = Transaction.VIP_OPTIONS[duration]

        if django_settings.IS_PYTHONANYWHERE:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "GoToGatewayView.post: django_settings.IS_PYTHONANYWHERE = True, so redirect to success_payment")
            user = MyUser.objects.get(email=request.user.email)
            user.is_vip = True
            user.vip_end_date = timezone.now() + timezone.timedelta(days=duration)
            user.save()
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"GoToGatewayView.post: user = {user}, user.is_vip = {user.is_vip}, user.vip_end_date = {user.vip_end_date}")
            return redirect(django_settings.SUCCESS_PAYMENT_REDIRECT_URL)


        factory = bankfactories.BankFactory()
        try:
            bank = factory.auto_create()
            bank.set_request(request)
            bank.set_amount(amount)
            bank.set_currency(CurrencyEnum.IRT)
            bank.set_client_callback_url(reverse('verify'))
            bank_record = bank.ready()

            tracking_code = bank_record.tracking_code

            # make a new Transaction
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                tracking_code=tracking_code,
                status=Transaction.PENDING,
                vip_duration=duration,
            )
            transaction.save()

            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"GoToGatewayView.post: user = {request.user}, amount = {amount}, tracking_code = {tracking_code}, status = {Transaction.PENDING}, vip_duration = {duration}")
            return bank.redirect_gateway()
        except AZBankGatewaysException as e:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), f"GoToGatewayView.post: AZBankGatewaysException = {e}, response = 404")
            return Response(status=HTTP_400_BAD_REQUEST)


class VerifyView(APIView):

    def get(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "VerifyView.get")
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
        if not tracking_code:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "VerifyView.get: tracking_code is None, response = 404")
            return Response(status=HTTP_400_BAD_REQUEST)
        try:
            transaction = Transaction.objects.get(tracking_code=tracking_code)
        except Transaction.DoesNotExist:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "VerifyView.get: Transaction.DoesNotExist, response = 404")
            return Response(status=HTTP_400_BAD_REQUEST)

        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "VerifyView.get: bank_models.Bank.DoesNotExist, response = 404")
            return Response(status=HTTP_400_BAD_REQUEST)

        if bank_record.is_success or True:
            transaction.status = Transaction.SUCCESS
            transaction.save()
            transaction.user.is_vip = True
            if transaction.user.vip_end_date is None:
                transaction.user.vip_end_date = timezone.now() + timezone.timedelta(days=transaction.vip_duration)
            else:
                transaction.user.vip_end_date += timezone.timedelta(days=transaction.vip_duration)

            transaction.user.save()

            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f'VerifyView.get: user = {transaction.user}, payment is success, user.is_vip = {transaction.user.is_vip}, user.vip_end_date = {transaction.user.vip_end_date}')

            if django_settings.IS_PYTHONANYWHERE:
                logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "VerifyView.get: django_settings.IS_PYTHONANYWHERE = True, so redirect to success_payment")
                return redirect(django_settings.SUCCESS_PAYMENT_REDIRECT_URL)
            else:
                return HttpResponse("پرداخت شما با موفقیت انجام شد. حساب کاربری شما به مدت {} روز فعال شد.".format(transaction.vip_duration))

        transaction.status = Transaction.FAILED
        transaction.save()

        if django_settings.IS_PYTHONANYWHERE:
            return redirect(django_settings.FAILED_PAYMENT_REDIRECT_URL)
        else:
            return HttpResponse(
                "پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.")


class VIPOptionsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    # return vip options and prices for each option
    def get(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "VIPOptionsView.get")
        return Response(Transaction.VIP_OPTIONS, status=HTTP_200_OK)
