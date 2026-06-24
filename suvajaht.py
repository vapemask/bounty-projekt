import subprocess
import os

def run_deep_scan():
    # Kontrollime, kas sisendfail on olemas
    if not os.path.exists("elusad.txt"):
        print("❌ Viga: 'elusad.txt' puudub. Jookse enne multijaht.py või loome selle!")
        return

    print("🚀 ALUSTAN SÜVASKANEERIMIST (Nuclei)...")
    print("🎯 Sihtmärkide arv:", sum(1 for line in open('elusad.txt')))

    # Nuclei käsk:
    # -l: loeb elusad lehed failist
    # -as: automaatne skaneerimine vastavalt tuvastatud tehnoloogiale (väga võimas!)
    # -severity critical,high: keskendume ainult suurtele leidudele
    # -o süvajaht_tulemused.txt: kuhu tulemused salvestada
    # -ni: non-interactive režiim (ei küsi küsimusi)
    
    cmd = "nuclei -l elusad.txt -as -severity critical,high -o süvajaht_tulemused.txt -ni"
    
    try:
        # Käivitame skaneerimise
        subprocess.run(cmd, shell=True, check=True)
        
        # Kontrollime, kas leiti midagi kriitilist
        if os.path.exists("süvajaht_tulemused.txt") and os.path.getsize("süvajaht_tulemused.txt") > 0:
            print("\n🔥 LEIDUD! Vaata faili 'süvajaht_tulemused.txt'.")
        else:
            print("\nClean scan. Seekord kriitilisi vigu ei leitud.")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Viga Nuclei käivitamisel (veakood {e.returncode}). Veendu, et Nuclei on installitud.")
    except Exception as e:
        print(f"❌ Ootamatu viga: {e}")

if __name__ == "__main__":
    run_deep_scan()