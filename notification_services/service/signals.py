from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q

from .models import Client, Message, Mailing
from .tasks import task_for_send_message


@receiver(post_save, sender=Mailing)
def create(sender, instance, created, **kwargs):
    if created:
        mailing = Mailing.objects.filter(id=instance.id).first()
        clients = Client.objects.filter(Q(mobile_operator_code=mailing.mobile_code) | Q(tag=mailing.client_tag)).all()
        for client in clients:
            Message.objects.create(status="Not sent", client_id=client.id, mailing_id=instance.id)
            message = Message.objects.filter(mailing_id=instance.id, client_id=client.id).select_related('client',
                                                                                                         'mailing').first()
            data = {"id": message.id, "phone_number": client.phone_number, "text": mailing.text}
            if instance.send:
                task_for_send_message.apply_async((data, client.id, mailing.id), expires=mailing.date_finish)
            else:
                task_for_send_message.apply_async((data, client.id, mailing.id), eta=mailing.date_start,
                                                                        expires=mailing.date_finish)