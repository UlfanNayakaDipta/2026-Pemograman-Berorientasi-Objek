# -*- coding: utf-8 -*-

# 1. FOR Loop dengan range()
print("1) FOR loop dengan range()")
for i in range(5):
    print("Perulangan ke-", i)

print()  # pemisah


# 2. FOR Loop untuk List
print("2) FOR loop mengiterasi list")
buah = ["apel", "mangga", "jeruk", "pisang"]
for item in buah:
    print("Buah:", item)

print()


# 3. WHILE Loop
print("3) WHILE loop sederhana")
count = 0
while count < 5:
    print("count =", count)
    count += 1

print()


# 4. BREAK
print("4) BREAK di dalam loop")
for i in range(10):
    if i == 3:
        print("Loop dihentikan pada i =", i)
        break
    print("i =", i)

print()


# 5. CONTINUE
print("5) CONTINUE di dalam loop")
for i in range(5):
    if i == 2:
        print("Lewati i =", i, "dengan continue")
        continue
    print("i =", i)