import tracemalloc
tracemalloc.start(10)

time1 = tracemalloc.take_snapshot()

import pandas as pd
x = pd.DataFrame([1,2,3])
time2 = tracemalloc.take_snapshot()

stats = time2.compare_to(time1, 'lineno')
for stat in stats[:3]:
  print(stat)
"""
Actual Output
<frozen importlib._bootstrap_external>:525: size=17.7 MiB (+17.7 MiB), count=165335 (+165335), average=112 B
<frozen importlib._bootstrap>:219: size=2502 KiB (+2502 KiB), count=20916 (+20916), average=122 B
/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/linecache.py:137: size=588 KiB (+588 KiB), count=5720 (+5720), average=105 B
"""
