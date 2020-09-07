import tracemalloc
tracemalloc.start(10)

time1 = tracemalloc.take_snapshot()

import pandas as pd
x = pd.DataFrame([1,2,3])
time2 = tracemalloc.take_snapshot()

stats = time2.compare_to(time1, 'traceback')
top = stats[0]
print('\n'.join(top.traceback.format()))
"""
Actual Output

  File "<frozen importlib._bootstrap>", line 677
  File "<frozen importlib._bootstrap_external>", line 728
  File "<frozen importlib._bootstrap>", line 219
  File "/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages/pandas/io/common.py", line 22
    import zipfile
  File "<frozen importlib._bootstrap>", line 983
  File "<frozen importlib._bootstrap>", line 967
  File "<frozen importlib._bootstrap>", line 677
  File "<frozen importlib._bootstrap_external>", line 724
  File "<frozen importlib._bootstrap_external>", line 857
  File "<frozen importlib._bootstrap_external>", line 525
"""
