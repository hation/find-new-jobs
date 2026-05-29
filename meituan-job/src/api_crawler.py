#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘API爬取器
按照夸克项目规范：API优先策略
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class MeituanAPICrawler:
    """美团招聘API爬