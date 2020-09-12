## BetterWay58
### 최적화하기 전에 프로파일하자

#### 핵심정리 (두괄식)
- 성능 저하를 일으키는 원인이 때로는 불분명하므로 파이썬 프로그램을 최적화하기 전에 프로파일해야한다.
- cProfile이 더 정확한 프로파일링 정보를 제공하므로 profile모듈 대신에 cProfile을 사용하자.
- Profile 객체의 runcall 매소드는 함수 호출 트리를 프로파일하는 데 필요한 모든 기능을 제공한다.
- Stats 객체는 프로그램 성능을 이해하는 데 필요한 프로파일링 정보를 선택하고 출력하는 기능을 제공한다.

***

파이썬의 동적 특징은 런타임 성능에서 놀랄만한 동작을 보여준다.
느릴 것처럼 보이는 연산이 실제론 생각보다 빠르다. (문자열 처리, 제너레이터 등등)
반면에 빠를거라고 생각했던 연산이 실제로 매~~~우 느리다. (속성 접근, 함수 호출)

그렇다고 해서 위 두개 분류가 항상 정확한건 아니다. 파이썬 프로그램을 느리게 만드는 요인이 불분명할 수 있다.

가장 좋은 방법은 최적화하기 전에 직관을 무시하고 직접 프로그램의 성능을 측정하는 것이다.
파이썬에는 프로그램의 어느 부분이 얼만큼의 실행 시간을 소비하는 지 파악할 수 있는 내장 프로파일러를 제공한다.
프로파일러를 사용하면 문제의 가장 큰 원인에 최적화 노력을 최대한 집중 할 수 있고,
속도에 영향을 주지 않는 부분은 무시할 수 있다.

예를 들어 프로그램의 알고리즘이 느린 이유를 알고 싶다고 한다.
다음은 삽입 정렬로 데이터 리스트를 정렬하는 함수이다.

~~~python
def insertion_sort(data):
  result = []
  for value in data:
    insert_value(result, value)
  return result
~~~

삽입 정렬의 핵심 매커니즘은 각 데이터의 삽입 지점을 찾는 함수다.
다음은 극히 비효율적인 insert_value 함수로, 입력 배열을 순차적으로 스캔한다.

~~~python
def insert_value(array, value):
  for i, existing in enumerate(array):
    if existing > value:
      array.insert(i, value)
      return
    array.append(value)
~~~

insertion_sort와 insert_value를 프로파일하려고 난수로 구성도니 데이터 집합을 생성하고,
프로파일러에 넘길 test함수를 정의한다.

~~~python
from random import randint

max_size = 10**4
data = [randint(0, max_size) for _ in range(max_size)]
test = lambda: insertion_sort(data)
~~~
파이썬은 두가지 내장 프로파일러를 제공한다.
하나는 순수 파이썬 프로파일이고, 다른 하나는 C확장 모듈(cProfile)이다.
cProfile은 프로파일 동안에 프로그램의 성능에 미치는 영향을 최소화 할 수 있어서 **더** 좋다.
순수 파이썬 프로파일러는 결과를 왜곡할 수 있을 만큼 부하가 크다

~~~
파이썬 프로그램을 프로파일할 때 측정 대상이 코드 자체이지 외부 시스템이 아니라는 점을 명확하게 헤야한다.
네트워크나 디스크의 리소스에 접근하는 함수를 주의하자.
이런 함수는 하부 시스템이 느리기 때문에 프로그램의 실행시간에 큰 영향을 줄 수 있다.

프로그램에서 이처럼 느린 리소스의 지연을 막으려고 캐시를 사용한다면,
프로파일링을 시작하기 전에 캐시가 적절히 동작하도록 준비해야한다.
~~~

cProfile 모듈의 Profile 객체를 생성하고 runcall 메소드로 테스트 함수를 실행해보자.

~~~python
profiler = Profile()
profiler.runcall(test)
~~~

테스트 함수의 실행이 끝나면 내장 모듈 pstats와 Stats 클래스로 함수의 성능 통계를 뽑을 수 있다.
Stats 객체의 다양한 메서드를 이용하면 프로파일 정보를 선택하고 정렬하는 방법을 조절해서
관심있는 정보만 볼 수 있다.

~~~python
stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats('cumulative')
stats.print_stats()
~~~

결과는 함수로 구성된 정보의 테이블이다.
데이터 샘플은 runcall 메서드가 실행되는 동안 프로파일러가 활성화되어 있을 때만 얻어온다.

~~~bash
실제 결과
         20003 function calls in 1.098 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    1.098    1.098 profiling.py:19(<lambda>)
        1    0.002    0.002    1.098    1.098 profiling.py:1(insertion_sort)
    10000    1.081    0.000    1.096    0.000 profiling.py:7(insert_value)
     9990    0.014    0.000    0.014    0.000 {method 'insert' of 'list' objects}
       10    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
~~~

프로파일러 통계 칼럼의 의미를 간략히 알아보자

- ncalls: 프로파일링 주기 동안 함수 호출 횟수
- tottime: 함수가 실행되는 동안 소비한 초 단위의 시간으로, 다른 함수 호출을 실행하는 데 걸린 시간은 배제된다.
- precall(tottime): 함수를 호출하는 데 걸린 평균 시간이며 초 단위이다. 다른 함수의 호출 시간은 배제된다. tottime을 ncalls로 나눈 값이다.
- cumtime: 함수를 실행하는 데 걸린 초 단위 누적 시간이며, 다른 함수를 호출하는 데 걸린시간도 포함한다.
- precall(cumtime): 함수를 호출 할 때마다 걸린 시간에 대한 초 단위 평균 시간이며, 다른 함수를 호출하는 데 걸린 시간도 포함한다. cumtime을 ncalls로 나눈 값이다.

앞의 프로파일러 통계 테이블을 보면 테스트에서 CPU를 가장 많이 사용한 부분은 insert_value 함수에서 소비한 시간이다.

이번에는 내장 모듈 bisect를 사용하도록 insert_value 함수를 재정의한다.
~~~python
from bisect import bisect_left

def insert_value(array, value):
    i = bisect_left(array, value)
    array.insert(i, value)
~~~

다시 프로파일러를 실행하여 새 프로파일러 통계를 생성한다.
새로운 함수는 더 빨라졌고 누적 시간은 이전의 insert_value 함수에 비해 거의 100배 이상 줄었다.

~~~bash
실행 결과
         30003 function calls in 0.025 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.025    0.025 profiling_better.py:18(<lambda>)
        1    0.002    0.002    0.025    0.025 profiling_better.py:1(insertion_sort)
    10000    0.003    0.000    0.023    0.000 profiling_better.py:9(insert_value)
    10000    0.015    0.000    0.015    0.000 {method 'insert' of 'list' objects}
    10000    0.005    0.000    0.005    0.000 {built-in method _bisect.bisect_left}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
~~~

때로는 전체 프로그램을 프로파일할 때 공통 유틸리티 함수에서 대부분의 실행시간을 소비할 수도 있다.
프로파일러의 기본 출력은 유틸리티 함수가 프로그램의 다른 부분에서 얼마나 많이 호출되는 지 보여주지 않기 때문에 이해하기가 어렵다.

예를 들어, 다음 my_utility 함수는 프로그램에 있는 다른 두 함수에서 반복적으로 호출된다.

~~~python
def my_utility(a, b):
    # ...
    pass

def first_func():
    for _ in range(1000):
        my_utility(4, 5)

def second_func():
    for _ in range(10):
        my_utility(1, 3)

def my_program():
    for _ in range(20):
        first_func()
        second_func()
~~~

이 코드를 프로파일하고 기본 print_stats출력을 사용하면 이해하기 어려운 통계 결과가 나온다.

~~~bash
실행결과
         20242 function calls in 0.005 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.005    0.005 profiling_utils_bad.py:13(my_program)
       20    0.003    0.000    0.005    0.000 profiling_utils_bad.py:5(first_func)
    20200    0.001    0.000    0.001    0.000 profiling_utils_bad.py:1(my_utility)
       20    0.000    0.000    0.000    0.000 profiling_utils_bad.py:9(second_func)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
~~~

my_utility 함수가 대부분의 실행 시간을 소비하는 원인이라는 게 명확하지만,
이 함수가 이렇게 많이 호출되는 이유는 명확하게 알기 어렵다.

프로그램 코드에서 찾는다면 my_utility가 여러 번 호출되고 있다는 사실을 알겠지만 여전히 이해하기 힘들다.

파이썬 프로파일러는 이 문제를 처리하려고 각 함수의 프로파일링 정보에 기여하는 호출자를 찾는 방법을 제공한다.

~~~python
stats.print_callers()
~~~

이 프로파일러 통계 테이블은 호출된 함수를 왼쪽에 보여주며, 누가 이런 호출을 하는 지를 오른쪽에 보여준다.

다음 통계 테이블은 my_utility가 first_func에 의해 가장 많이 사용되었음을 명확하게 알려준다.

~~~bash
실행 결과
   Ordered by: cumulative time

Function                                          was called by...
                                                      ncalls  tottime  cumtime
profiling_utils_bad.py:13(my_program)             <-
profiling_utils_bad.py:5(first_func)              <-      20    0.003    0.005  profiling_utils_bad.py:13(my_program)
profiling_utils_bad.py:1(my_utility)              <-   20000    0.001    0.001  profiling_utils_bad.py:5(first_func)
                                                         200    0.000    0.000  profiling_utils_bad.py:9(second_func)
profiling_utils_bad.py:9(second_func)             <-      20    0.000    0.000  profiling_utils_bad.py:13(my_program)
{method 'disable' of '_lsprof.Profiler' objects}  <-
~~~
