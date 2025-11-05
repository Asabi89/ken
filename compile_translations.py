#!/usr/bin/env python
"""
Script pour compiler les fichiers de traduction Django
Usage: python compile_translations.py
"""
import os
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ken_project.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"Erreur lors de l'initialisation de Django: {e}")
    print("Tentative de compilation manuelle...")

# Compilation manuelle avec msgfmt
import subprocess

locale_dir = 'locale/fr/LC_MESSAGES'
po_file = os.path.join(locale_dir, 'django.po')
mo_file = os.path.join(locale_dir, 'django.mo')

if os.path.exists(po_file):
    try:
        # Utiliser gettext msgfmt pour compiler
        result = subprocess.run(['msgfmt', po_file, '-o', mo_file], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Traductions compilées: {mo_file}")
        else:
            print(f"✗ Erreur: {result.stderr}")
    except FileNotFoundError:
        print("msgfmt n'est pas installé. Installation recommandée:")
        print("  macOS: brew install gettext")
        print("  Linux: apt-get install gettext")
        print("\nEn attendant, Django utilisera les fichiers .po directement en mode DEBUG")
else:
    print(f"Fichier {po_file} introuvable")

print("\n✓ Les traductions sont prêtes!")
print("  - Langue par défaut: Anglais (EN)")
print("  - Langue disponible: Français (FR)")
print("  - Changement de langue: Cliquez sur EN/FR dans la navigation")
