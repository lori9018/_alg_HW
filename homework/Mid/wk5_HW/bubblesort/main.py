from bubble_sort_fp import bubble_sort, my_map, my_filter, my_reduce

# 排序
print(bubble_sort([5, 1, 4, 2, 8]))        # [1, 2, 4, 5, 8]

# 排序字串也可以（Python 能比較大小的型別都行）
print(bubble_sort(["pear", "apple", "fig"]))  # ['apple', 'fig', 'pear']

# 單獨使用自製的高階函數
print(my_map(lambda x: x * 2, [1, 2, 3]))            # [2, 4, 6]
print(my_filter(lambda x: x > 2, [1, 2, 3, 4]))      # [3, 4]
print(my_reduce(lambda a, b: a + b, [1, 2, 3], 0))   # 6