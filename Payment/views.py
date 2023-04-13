import logging

from azbankgateways import bankfactories
from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways.models import CurrencyEnum, BankType
from django.conf import settings
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from MyUser.models import MyUser
from .models import Transaction
from azbankgateways import bankfactories, models as bank_models, default_settings as settings


from MyUser.permissions import OwnProfilePermission


class GoToGatewayView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        OwnProfilePermission
    ]

    def post(self, request):
        duration = request.data.get('duration', None)
        duration = int(duration)

        if duration is None or duration not in Transaction.VIP_OPTIONS:
            raise Http404

        amount = Transaction.VIP_OPTIONS[duration]

        # print all logging
        # logging.basicConfig(level=logging.DEBUG)

        factory = bankfactories.BankFactory()
        try:
            bank = factory.auto_create()
            bank.set_request(request)
            bank.set_amount(amount)
            bank.set_currency(CurrencyEnum.IRT)
            bank.set_client_callback_url(reverse('verify'))
            bank_record = bank.ready()

            tracking_code = bank_record.tracking_code

            print('tracking_code: ', tracking_code)

            # make a new Transaction
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                tracking_code=tracking_code,
                status=Transaction.PENDING,
                vip_duration=duration,
            )
            transaction.save()

            # هدایت کاربر به درگاه بانک
            return bank.redirect_gateway()
        except AZBankGatewaysException as e:
            logging.critical(e)
            # TODO: redirect to failed page.
            raise e


class VerifyView(APIView):

    def get(self, request):
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
        print('verify: ', tracking_code)
        if not tracking_code:
            raise Http404
        try:
            transaction = Transaction.objects.get(tracking_code=tracking_code)
        except Transaction.DoesNotExist:
            raise Http404

        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            raise Http404

        print(bank_record.status)
        print(bank_record.extra_information)


        if bank_record.is_success or True:
            transaction.status = Transaction.SUCCESS
            transaction.save()
            transaction.user.is_vip = True
            if transaction.user.vip_end_date is None:
                transaction.user.vip_end_date = timezone.now() + timezone.timedelta(days=transaction.vip_duration)
            else:
                transaction.user.vip_end_date += timezone.timedelta(days=transaction.vip_duration)

            transaction.user.save()

            print(transaction.user.email)
            return HttpResponse("پرداخت شما با موفقیت انجام شد. حساب کاربری شما به مدت {} روز فعال شد.".format(transaction.vip_duration))

        transaction.status = Transaction.FAILED
        transaction.save()

        return HttpResponse(
            "پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.")


class VIPOptionsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    # return vip options and prices for each option
    def get(self, request):
        return Response(Transaction.VIP_OPTIONS, status=HTTP_200_OK)
