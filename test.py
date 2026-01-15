import bisect

def specialArray(nums: list[int]) -> int:
    nums = sorted(nums)
    n = len(nums)
    for i in range(n, 0, -1):
        k = bisect.bisect_left(nums, i)
        if(n - k == i):
            return i
    return -1

    
print(specialArray([0,4,3,0,4]))

import timeit

# Вимірювання часу для першої функції
time1 = timeit.timeit("specialArray([0,4,3,0,4])", globals=globals(), number=100000)
print(f"specialArray виконалась за {time1:.6f} секунд (1000 повторів)")
