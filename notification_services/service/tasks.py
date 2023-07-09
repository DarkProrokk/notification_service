import os
import time
import pytz
from dotenv import load_dotenv
from celery.utils.log import get_task_logger
import requests
from .models import Message, Client, Mailing
from celery_app import app
from datetime import datetime
logger = get_task_logger(__name__)

load_dotenv()
URL = os.getenv("URL")
TOKEN = os.getenv("TOKEN")

@app.task(bind=True)
def task_for_send_message(self, data, client_id, mailing_id, url=URL, token=TOKEN):
    client = Client.objects.get(pk=client_id)
    mailing = Mailing.objects.get(pk=mailing_id)
    client_time = datetime.now(pytz.timezone(client.timezone)).time()
    mail_id = data['id']
    header = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'}
    if mailing.time_interval_start <= client_time <= mailing.time_interval_finish:
        try:
            print(requests.post(url=url + str(mail_id), headers=header, json=data).status_code)
            if requests.post(url=url + str(mail_id), headers=header, json=data).status_code != 200:
                raise ConnectionError
            else:
                requests.post(url=url + str(mail_id), headers=header, json=data)
        except requests.exceptions.RequestException as exc:
            Message.objects.filter(pk=mail_id).update(status="Failed")
            raise self.retry(exc=exc)
        except ConnectionError:
            Message.objects.filter(pk=mail_id).update(status="Failed")
        else:
            Message.objects.filter(pk=mail_id).update(status="Sent")



