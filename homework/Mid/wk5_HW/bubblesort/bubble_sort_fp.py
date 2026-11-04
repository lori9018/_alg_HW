"""
自製 map / filter / reduce（只用遞迴），並用它們完成「無迴圈」的泡沫排序。
全檔不使用 for / while / 推導式 / 內建 map、filter、reduce、sorted。
"""
import random


# ---------------------------------------------------------------
# 1. 自製高階函數（遞迴）
# ---------------------------------------------------------------
def my_map(f, xs):
    """my_map(f, [a,b,c]) -> [f(a), f(b), f(c)]"""
    if not xs:                                   # base case
        return []
    return [f(xs[0])] + my_map(f, xs[1:])


def my_filter(pred, xs):
    """保留 pred(x) 為 True 的元素"""
    if not xs:
        return []
    head, tail = xs[0], my_filter(pred, xs[1:])
    return [head] + tail if pred(head) else tail


def my_reduce(f, xs, init):
    """my_reduce(f, [a,b,c], z) = f(f(f(z,a),b),c)  (左摺疊)"""
    if not xs:
        return init
    return my_reduce(f, xs[1:], f(init, xs[0]))


def my_zip(xs, ys):
    if not xs or not ys:
        return []
    return [(xs[0], ys[0])] + my_zip(xs[1:], ys[1:])


# ---------------------------------------------------------------
# 2. 泡沫排序
# ---------------------------------------------------------------
def bubble_pass(lst):
    """
    做「一趟」泡沫：由左到右比較相鄰元素，逆序就交換。
    用 reduce 實作：acc 的最後一個元素是「正在往右冒的泡」(carry)。
        carry > x  -> x 放前面，carry 繼續往右帶
        否則       -> carry 放下，x 變成新的 carry
    一趟結束後，最大值一定在最尾端。
    """
    if len(lst) < 2:
        return lst

    def step(acc, x):
        carry = acc[-1]
        return acc[:-1] + ([x, carry] if carry > x else [carry, x])

    return my_reduce(step, lst[1:], [lst[0]])


def is_sorted(lst):
    """用 zip + filter：找出所有逆序的相鄰對，沒有就代表已排序"""
    pairs = my_zip(lst[:-1], lst[1:])
    return my_filter(lambda p: p[0] > p[1], pairs) == []


def bubble_sort(lst):
    """重複做 bubble_pass，直到沒有逆序為止（遞迴取代外層迴圈）"""
    if is_sorted(lst):
        return lst
    return bubble_sort(bubble_pass(lst))


# ---------------------------------------------------------------
# 3. 測試（同樣不用迴圈）
# ---------------------------------------------------------------
if __name__ == "__main__":
    print(my_map(lambda x: x * x, [1, 2, 3, 4]))               # [1, 4, 9, 16]
    print(my_filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5, 6]))  # [2, 4, 6]
    print(my_reduce(lambda a, b: a + b, [1, 2, 3, 4], 0))       # 10

    print(bubble_pass([5, 1, 4, 2, 8]))                         # [1, 4, 2, 5, 8]
    print(bubble_sort([5, 1, 4, 2, 8]))                         # [1, 2, 4, 5, 8]
    print(bubble_sort([]), bubble_sort([7]), bubble_sort([3, 3, 1, 2, 2]))

    # 隨機測試：與內建 sorted 比對（用 my_map 取代 for）
    def check(seed):
        random.seed(seed)
        data = my_map(lambda _: random.randint(-50, 50), [0] * 30)
        return bubble_sort(data) == sorted(data)

    results = my_map(check, [0] * 0 + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print("隨機測試全部通過:", my_reduce(lambda a, b: a and b, results, True))