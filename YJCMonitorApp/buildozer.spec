[app]

title = YJC Monitor
package.name = yjcmonitor
package.domain = org.chbyjc

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy==2.3.1,requests,feedparser,beautifulsoup4,soupsieve,urllib3,idna,certifi,charset-normalizer,plyer,pyjnius

orientation = portrait
fullscreen = 0

# آیکون و اسپلش (اختیاری) - اگر فایل icon.png / presplash.png را
# در کنار این فایل قرار دادید، خط‌های زیر را از حالت کامنت خارج کنید:
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

android.permissions = INTERNET, POST_NOTIFICATIONS, WAKE_LOCK

android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True

[buildozer]

log_level = 2
warn_on_root = 1
