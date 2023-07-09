from rest_framework import status, mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, render
from .models import Client, Message, Mailing
from .serializers import ClientSerializer, MessageSerializer, MailingSerializer
# from .tasks import recipients


class ClientViewSet(viewsets.ModelViewSet):

    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class MessageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class MailingViewSet(viewsets.ModelViewSet):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer

    @action(detail=True, methods=["get"])
    def info(self, request, pk=None):
        queryset_mailing = Mailing.objects.all()
        get_object_or_404(queryset_mailing, pk=pk)
        queryset = Message.objects.filter(mailing_id=pk).all()
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def full_info(self, request):
        count_mailings = Mailing.objects.count()
        mailing = Mailing.objects.values("id")
        result = {}
        res_for_all_mailings = {"Sent": 0, "Not sent": 0, "Failed": 0}
        for row in mailing:
            res_for_mailing = {}
            mail = Message.objects.filter(mailing_id=row["id"]).all()
            total_sent = mail.filter(status="Sent").count()
            total_not_sent = mail.filter(status="Not sent").count()
            total_failed = mail.filter(status="Failed").count()
            res_for_mailing["total_messages"] = len(mail)
            res_for_mailing["Sent"] = total_sent
            res_for_mailing["Not sent"] = total_not_sent
            res_for_mailing["Failed"] = total_failed
            res_for_all_mailings["Sent"] += total_sent
            res_for_all_mailings["Not sent"] += total_not_sent
            res_for_all_mailings["Failed"] += total_failed
            result[row["id"]] = res_for_mailing
        content = {"result_for_all_mailings": res_for_all_mailings, "count_mailings": count_mailings}
        content["result_for_target_mailings"] = result
        return Response(content)