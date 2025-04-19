import pandas as pd
import re
from pandas.api import types as ptypes

# Fungsi untuk membaca file Excel dan mengambil hanya kolom yang diperlukan
def baca_data_excel(path):
    try:
        data = pd.read_excel(path, header=0)
        # Hapus kolom duplikat
        data = data.loc[:, ~data.columns.duplicated()]
        # Pilih hanya kolom yang valid
        data = data[['Judul Paper', 'Tahun Terbit', 'Nama Penulis']]
        return data
    except Exception as e:
        print(f"Gagal membaca file Excel: {e}")
        return None

# Fungsi normalisasi teks (untuk pencarian robust)
def normalize_text(text):
    if pd.isnull(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Hapus simbol, hanya huruf/angka/spasi
    text = re.sub(r'\s+', ' ', text)  # Ganti spasi berlebihan
    return text.strip()

# Linear Search
def linear_search(data, kolom, keyword):
    keyword_norm = normalize_text(keyword)
    return data[data[kolom].apply(lambda x: keyword_norm in normalize_text(x))]

# Binary Search
def binary_search(data, kolom, keyword):
    data_sorted = data.sort_values(by=kolom, ascending=True).reset_index(drop=True)
    hasil = pd.DataFrame(columns=data.columns)
    keyword_norm = normalize_text(keyword)

    if ptypes.is_numeric_dtype(data[kolom]):
        try:
            key_val = float(keyword)
        except ValueError:
            return hasil
        low, high = 0, len(data_sorted) - 1
        while low <= high:
            mid = (low + high) // 2
            mid_val = data_sorted.at[mid, kolom]
            if mid_val == key_val:
                hasil = pd.concat([hasil, data_sorted.iloc[[mid]]])
                i = mid - 1
                while i >= 0 and data_sorted.at[i, kolom] == key_val:
                    hasil = pd.concat([hasil, data_sorted.iloc[[i]]]); i -= 1
                i = mid + 1
                while i < len(data_sorted) and data_sorted.at[i, kolom] == key_val:
                    hasil = pd.concat([hasil, data_sorted.iloc[[i]]]); i += 1
                break
            elif mid_val < key_val:
                low = mid + 1
            else:
                high = mid - 1
    else:
        data_sorted['normalized'] = data_sorted[kolom].apply(normalize_text)
        low, high = 0, len(data_sorted) - 1
        while low <= high:
            mid = (low + high) // 2
            mid_val = data_sorted.at[mid, 'normalized']
            if mid_val == keyword_norm:
                hasil = pd.concat([hasil, data_sorted.iloc[[mid]]])
                i = mid - 1
                while i >= 0 and data_sorted.at[i, 'normalized'] == keyword_norm:
                    hasil = pd.concat([hasil, data_sorted.iloc[[i]]]); i -= 1
                i = mid + 1
                while i < len(data_sorted) and data_sorted.at[i, 'normalized'] == keyword_norm:
                    hasil = pd.concat([hasil, data_sorted.iloc[[i]]]); i += 1
                break
            elif mid_val < keyword_norm:
                low = mid + 1
            else:
                high = mid - 1

    return hasil.drop(columns='normalized', errors='ignore')

# Fungsi untuk mencetak hasil
def print_results(hasil):
    if hasil.empty:
        print("\nData tidak ditemukan.")
        return

    print("\nHasil pencarian:")
    print(f"{'Judul Paper':<50} {'Tahun':<6} {'Penulis':<40}")
    print("-" * 100)
    for _, row in hasil.iterrows():
        judul = row['Judul Paper']
        if len(judul) > 50:
            judul = judul[:47] + '...'

        tahun = str(int(row['Tahun Terbit']))
        penulis = str(row['Nama Penulis']).replace(';', ', ')
        if len(penulis) > 40:
            penulis = penulis[:37] + '...'

        print(f"{judul:<50} {tahun:<6} {penulis:<40}")

# Program Utama
def main():
    file_path = "C:/Users/Erlangga/Documents/UTS/Struktur_Data_Dataset_Kelas_A_B_C.xlsx"
    data = baca_data_excel(file_path)
    if data is None:
        return

    while True:
        print("\nPilih metode pencarian:")
        print("0. Keluar")
        print("1. Linear Search")
        print("2. Binary Search")
        metode = input("Pilihan (0/1/2): ")

        if metode == "0":
            print("Program selesai. Terima kasih!")
            break
        if metode not in ("1", "2"):
            print("Metode tidak valid, silakan pilih lagi.")
            continue

        print("\nPilih kolom pencarian:")
        print("1. Judul Paper")
        print("2. Tahun Terbit")
        print("3. Nama Penulis")
        pilihan = input("Pilihan (1/2/3): ")
        kolom_dict = {"1": "Judul Paper", "2": "Tahun Terbit", "3": "Nama Penulis"}
        kolom = kolom_dict.get(pilihan)
        if not kolom:
            print("Pilihan kolom tidak valid, silakan ulangi.")
            continue

        keyword = input(f"Masukkan kata kunci di kolom '{kolom}': ")

        if metode == "1":
            hasil = linear_search(data, kolom, keyword)
        else:
            hasil = binary_search(data, kolom, keyword)

        print_results(hasil)

if __name__ == "__main__":
    main()
