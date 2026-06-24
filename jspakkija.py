import re
import jsbeautifier
import json
import os
import sys

class JSChunkUnpacker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = ""
        self.beautified_content = ""
        
        # Regulaaravaldised erinevate tundlike andmete leidmiseks
        self.patterns = {
            "google_oauth_client_id": r"\d+-[a-z0-9]+\.apps\.googleusercontent\.com",
            "api_key": r"(?:api_key|apikey|secret|token)[\"']?\s*[:=]\s*[\"']([a-zA-Z0-9_\-]{16,})[\"']",
            "urls": r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+",
            "firebase_config": r"apiKey:\s*[\"'].*?[\"'],\s*authDomain:\s*[\"'].*?[\"']",
            "email_addresses": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        }

    def load_file(self):
        """Laeb JS faili sisu."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"[+] Fail '{self.file_path}' edukalt laetud.")
        except Exception as e:
            print(f"[!] Viga faili laadimisel: {e}")
            sys.exit(1)

    def beautify(self):
        """Muudab minifitseeritud JS koodi loetavaks."""
        print("[*] Koodi de-minifitseerimine (beautify)...")
        options = jsbeautifier.default_options()
        options.indent_size = 2
        self.beautified_content = jsbeautifier.beautify(self.content, options)
        
        # Salvestame loetava versiooni
        output_name = self.file_path.replace(".js", ".pretty.js")
        with open(output_name, 'w', encoding='utf-8') as f:
            f.write(self.beautified_content)
        print(f"[+] Loetav kood salvestatud: {output_name}")

    def extract_intel(self):
        """Otsib koodist huvipakkuvaid andmeid."""
        print("[*] Luurandmete (intel) ekstraktimine...")
        results = {}
        
        for key, pattern in self.patterns.items():
            found = re.findall(pattern, self.content, re.IGNORECASE)
            if found:
                # Eemaldame duplikaadid
                results[key] = list(set(found))
        
        return results

    def run(self):
        self.load_file()
        self.beautify()
        intel = self.extract_intel()
        
        print("\n=== LEITUD LUURANDMED ===")
        for category, items in intel.items():
            print(f"\n[!] {category.upper()}:")
            for item in items:
                print(f"  - {item}")
        
        # Salvestame tulemused JSON faili
        report_name = self.file_path.replace(".js", ".intel.json")
        with open(report_name, 'w', encoding='utf-8') as f:
            json.dump(intel, f, indent=4)
        print(f"\n[+] Aruanne salvestatud: {report_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kasutamine: python3 js_analyser.py <faili_nimi.js>")
    else:
        # Enne käivitamist installi: pip install jsbeautifier
        analyser = JSChunkUnpacker(sys.argv[1])
        analyser.run()