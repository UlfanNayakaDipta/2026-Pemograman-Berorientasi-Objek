# -*- coding: utf-8 -*-

# 1. Pendeklarasian Variabel
nama = "Ulfan"
umur = 18
tinggi = 170.5
is_student = True

print("Nama =", nama)
print("Umur =", umur)
print("Tinggi =", tinggi, "cm")
print("Mahasiswa =", is_student)

# 2. Operasi Aritmetika
a = 10
b = 3

penjumlahan = a + b
pengurangan = a - b
perkalian = a * b
pembagian = a / b
pembagian_bulat = a // b
modulus = a % b
pangkat = a ** b

print("\nOPERASI ARITMETIKA")
print("a =", a, ", b =", b)
print("Penjumlahan =", penjumlahan)
print("Pengurangan =", pengurangan)
print("Perkalian =", perkalian)
print("Pembagian =", pembagian)
print("Pembagian Bulat =", pembagian_bulat)
print("Modulus =", modulus)
print("Pangkat =", pangkat)

# 3. Operasi Perbandingan
lebih_besar = a > b
kurang_dari = a < b
sama_dengan = a == b
tidak_sama = a != b
lebih_besar_sama = a >= b
kurang_sama = a <= b

print("\nOPERASI PERBANDINGAN")
print("a > b =", lebih_besar)
print("a < b =", kurang_dari)
print("a == b =", sama_dengan)
print("a != b =", tidak_sama)
print("a >= b =", lebih_besar_sama)
print("a <= b =", kurang_sama)

# 4. Operasi Logika
x = True
y = False

logika_and = x and y
logika_or = x or y
logika_not_x = not x

print("\nOPERASI LOGIKA")
print("x =", x, ", y =", y)
print("x and y =", logika_and)
print("x or y =", logika_or)
print("not x =", logika_not_x)

# 5. Percabangan
if a > b and b > 0:
    print("\nKondisi terpenuhi: a lebih besar dari b, dan b masih positif.")
else:
    print("\nKondisi tidak terpenuhi atau b <= 0.")