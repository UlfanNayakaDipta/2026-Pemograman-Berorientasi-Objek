# -*- coding: utf-8 -*-

# 1. IF Sederhana
nilai = 85
print("Contoh IF Sederhana:")
if nilai > 80:
    print("Selamat! Anda lulus dengan nilai tinggi.\n")


# 2. IF-ELSE
umur = 17
print("Contoh IF-ELSE:")
if umur >= 18:
    print("Anda sudah cukup umur untuk mendapatkan SIM.")
else:
    print("Anda belum cukup umur untuk mendapatkan SIM.\n")


# 3. IF-ELIF-ELSE
hari = "Rabu"
print("Contoh IF-ELIF-ELSE:")
if hari == "Senin":
    print("Hari Senin - Saatnya kembali bekerja!")
elif hari == "Selasa":
    print("Hari Selasa - Jadwal rapat mingguan.")
elif hari == "Rabu":
    print("Hari Rabu - Ada diskon di beberapa toko.")
else:
    print("Hari lainnya - Atur jadwalmu dengan baik.\n")


# 4. IF Bersarang (Nested IF)
suhu = 35
print("Contoh IF Bersarang (Nested IF):")
if suhu > 30:
    print("Cuaca cukup panas.")
    if suhu > 40:
        print("Bahkan sangat terik! Disarankan banyak minum air.")
    else:
        print("Masih relatif normal, tapi tetap jaga kesehatan.")
else:
    print("Cuaca sepertinya cukup sejuk.\n")


# 5. IF dengan Operasi Logika
nilai_teori = 75
nilai_praktik = 80
print("Contoh IF dengan Operasi Logika AND/OR:")
if nilai_teori >= 70 and nilai_praktik >= 70:
    print("Anda lulus karena nilai teori dan praktik memadai.")
elif nilai_teori < 70 and nilai_praktik < 70:
    print("Anda perlu meningkatkan nilai teori dan praktik.")
elif nilai_teori < 70:
    print("Anda perlu meningkatkan nilai teori.")
else:
    print("Anda perlu meningkatkan nilai praktik.\n")


# 6. If Ternary
angka = -5
print("Contoh If Ternary (Conditional Expression):")
status = "Positif" if angka > 0 else "Negatif atau Nol"
print("Angka =", angka, "=>", status)