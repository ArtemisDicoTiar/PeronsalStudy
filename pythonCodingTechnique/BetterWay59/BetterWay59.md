## Better way 59
### tracemalloc으로 메모리 사용 현황과 누수를 파악하자

#### 핵심정리 (두괄식)
- 파이썬 프로그램이 메모리를 어떻게 사용하고, 메모리 누수를 일으키는지를 이해하기는 어렵다.
- gc모듈은 어떤 객체가 존재하는지를 이해하는 데 도움을 주지만, 해당 객체가 어떻게 할당되었는 지에 대한 정보는 제공하지 않는다.
- 내장 모듈 tracemalloc은 메모리 사용량의 근원을 이해하는 데 필요한 강력한 도구를 제공한다.
- 안타깝게도 파이썬3.4이상이어야만 사용할 수 있다.

***

CPython의 기본 구현은 참조 카운팅 (reference counting)으로 메모리를 관리한다.

* 참조 카운팅은 객체의 참조가 모두 해제되면 해당 객체가 정리되는 것을 보장함.
* 싸이썬은 자기 참조 객체가 가비지 컬렉션되는 것을 보장하는 Cycle Detector도 가지고 있다.
-> 기존 C 언어처럼 malloc해서 동적할당하고 직접 메모리할당 해제하는 방식으로 관리하지 안하도 됨을 의미.

그렇기 때문에 이론상 대부분의 파이썬 프로그래머는 프로그램 안에서 발생하는 메모리할당과 해제를 don't care해도 된다.
언어 차원에서 그리고 싸이썬 런타임에서 알아서 처리해준다.

하지만 실제로 프로그램은 referencing때문에 메모리 부족에 처한다.
파이썬 프로그램이
* 어디서 메모리를 사용하는 지
* 어디서 메모리 누수를 일으키는 지를 찾아내는 것
-> 어려운 과제이다.

메모리 사용을 디버깅하는 방법
1. 내장 모듈 gc (-> garbage collector)에 요청하여 가비지 컬렉터에 알려진 모든 객체를 나열.
* gc가 정확한 도구는 아니지만 이 방법을 사용하면 프로그램의 메모리가 어디서 사용되는 지 금방 알 수 있다.

eg.
~~~python
# using_gc.py
import gc
found_objects = gc.get_objects()
print('%d objects before' % len(found_objects))

import waste_memory
x = waste_memory.run()
found_objects = gc.get_objects()
print('%d objects after' % len(found_objects))

for obj in found_objects[:3]:
  print(repr(obj)[:100])

>>>
someAmountof objects before
someLargeAmountof objects after
<waste_memory.MyObject object at someMemoryAddress>
<waste_memory.MyObject object at someMemoryAddress>
<waste_memory.MyObject object at someMemoryAddress>
~~~

gc.get_objects를 사용할 때 문제는 객체가 어떻게 할당되는 지 아무런 정보가 없다.
-> 그냥 뭔 객체가 어디의 메모리를 차지하고 있다. 정도만 나옴. (외부 객체를 사용하던 빌트인 메소드를 이용해서 객체를 만들던)

복잡한 프로그램에서는 객체의 특정 클래스가 여러방법으로 할당될 수 있다.
(앞서 말한 것처럼 다른 파일를 import해서 가져올 수도 있고 외부 라이브러리, 모듈을 추가해서 객체를 만들 수도 있다.)

전체 객체 개수보다 메모리 누수가 있는 객체를 할당한 코드를 찾는 게 더 중요하다.

Python3.4 or upper 버전에서는 새 내장모듈 tracemalloc을 이용해서 해결할 수 있다.
tracemalloc은 객체가 할당된 위치에 연결할 수 있도록 해준다.

eg. tracemalloc을 사용하여 프로그램에서 메모리를 가장 많이 사용하는 세부분을 출력
~~~python
#top_n.py
import tracemalloc
tracemalloc.start(10)

time1 = tracemalloc.take_snapshot()

import pandas as import pd
x = pd.DataFrame([1,2,3])
time2 = tracemalloc.take_snapshot()

stats = time2.compare_to(time1, 'lineno')
for stat in stats[:3]:
  print(stat)

>>>
someRunFile:someLine: size=someSize (+ someSize), count=someNum (+someNum), average=someMemorySize
someRunFile:someLine: size=someSize (+ someSize), count=someNum (+someNum), average=someMemorySize
someRunFile:someLine: size=someSize (+ someSize), count=someNum (+someNum), average=someMemorySize
~~~

어떤 객체들이 프로그램 메모리 사용량을 주로 차지하고, 소스 코드의 어느부분에서 할당되는지를 쉽게 알 수 있다.
(어떤 프로그램의 어떤 라인에서 객체 사용이 발생하고 메모리 사용량이 나옴.)

tracemalloc 모듈은 각 할당의 전체 스택 트레이스도 출력할 수 있다.
(start 메소드에 넘긴 프레임 개수까지.)

eg. 프로그램에서 메모리 사용량의 가장 큰 근원이 되는 부분의 스택 트레이스를 출력한다.
~~~python
# with_trace.py
# ... -> top_n.py
stats = time2.compare_to(time1, 'traceback')
top = stats[0]
print('\n'.join(top.traceback.format()))

>>>
File "someFileName", line someNum
  someObject = someMethod
File "someFileName", line someNum
  someObject = someMethod
File "someFileName", line someNum
  someObject = someMethod
~~~

이와 같이 스택트레이스는 공통함수의 어느 부분이 프로그램의 메모리를 많이 소비하는 지 알아내는 데 가장 중요한 정보다.

안타깝게도 파이썬2에서는 제공하지 않는다. (요즘에 파이썬2로 작성된 프로그램이나 작성되는 프로그램을 본 적 없음. 아! 플라스크 기초 프로그램이 2버전으로 구동되었던 거 같음.)
