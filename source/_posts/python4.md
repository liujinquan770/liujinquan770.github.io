---
title: PYTHON笔记4 定时任务工具apscheduler
date: 2018-07-03 14:57:43
modified: 2018-07-10 14:15:43
tags: [python]
categories: python
---

python中类似quartz的定时任务框架

![示例图片](python4/2018073.jpg)

<!--more-->

暂时记录一段代码方便以后参考，具体使用参考[http://www.cnblogs.com/luxiaojun/p/6567132.html](http://www.cnblogs.com/luxiaojun/p/6567132.html)

``` python
from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler


def tick():
    print('Tick! The time is: %s' % datetime.now())


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(tick, 'interval', seconds=3)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

```
