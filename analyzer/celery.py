from __future__ import absolute_import
from celery import Celery
import logging

from analyzer import BROKER_URL

logger = logging.getLogger(__name__)

app = Celery('story-analyzer',
             broker=BROKER_URL,
             # backend="db+sqlite:///celery-backend.db",
             include=['analyzer.tasks'])
