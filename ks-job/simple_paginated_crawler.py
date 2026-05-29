#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘简单分页爬取器
使用直接的方法翻页获取所有数据
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Any,