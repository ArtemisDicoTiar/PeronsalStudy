import gc
found_objects = gc.get_objects()
print('%d objects before' % len(found_objects))

import pandas as pd

test = pd.DataFrame([1,2,3])

found_objects = gc.get_objects()
print('%d objects after' % len(found_objects))

for obj in found_objects[:3]:
  print(repr(obj)[:100])

"""
Actual Output

5708 objects before
58958 objects after
{<weakref at 0x7f8d018ff710; to 'type' at 0x10ad06c90 (int)>}
<weakref at 0x7f8d018ff6b0; to 'set' at 0x7f8d01902140>
<built-in method _destroy of weakref object at 0x7f8d018ff6b0>
"""
