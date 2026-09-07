[app]

title = Quiz App
package.name = quizapp
package.domain = org.eni.quizapp

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,certifi,urllib3,charset_normalizer,idna

orientation = portrait
fullscreen = 0

# Décommente et ajoute un fichier icon.png (carré, ex: 512x512) dans mobile/ si tu
# veux une icône personnalisée. Sans ça, Buildozer utilise une icône par défaut.
# icon.filename = %(source.dir)s/icon.png

android.permissions = INTERNET

# API Android ciblée / minimale — valeurs standards recommandées par Buildozer
android.api = 34
android.minapi = 21
android.ndk = 25b

# Architecture : arm64-v8a couvre l'immense majorité des téléphones récents.
# Ajoute armeabi-v7a si tu dois supporter d'anciens appareils 32 bits.
android.archs = arm64-v8a

android.allow_backup = True

[buildozer]

log_level = 2
warn_on_root = 1
