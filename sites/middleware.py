# -*- coding: utf-8 -*-
import logging
import traceback
import StringIO
from django.utils import simplejson as json

logger_request = logging.getLogger('django.request')
logger_response = logging.getLogger('django.response')
logger_error = logging.getLogger('django.error')


