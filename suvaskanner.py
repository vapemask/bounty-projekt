import subprocess, os

def run_deep_scan():
    if not os.path.exists("elusad.txt"):
        print("❌ Viga: 'elusad.txt' puudub. Jookse enne multijaht.py!")
        return

    print("🚀 ALUSTAN SÜVASKANEERIMIST (Nuclei)...")
    
    # Nuclei käsk:
    # -l: loeb elusad lehed
    # -as: automaatne skaneerimine vastavalt tehnoloogiale
    # -severity critical,high: otsib ainult kõige kallimaid vigu
    # -o süvajaht_tulemused.txt: salvestab raporti
    
    cmd = "nuclei -l elusad.txt -as -severity critical,high -o süvajaht_tulemused.txt"
    
    try:
        subprocess.run(cmd, shell=True)
        print("\n✅ Süvaskaneerimine lõppenud! Vaata faili 'süvajaht_tulemused.txt'.")
    except Exception as e:
        print(f"❌ Viga Nuclei käivitamisel: {e}")

if __name__ == "__main__":
    run_deep_scan()