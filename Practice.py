def bubble_sort_visual(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                print(f"Swapped: {arr}") # <--- Watch the numbers move!
    return arr

bubble_sort_visual([5, 1, 4, 2, 8])