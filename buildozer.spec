[app]
title = Parastar
package.name = parastar
package.domain = org.parastar
source.dir = .
source.include_exts = py,ttf,wav,png,jpg,jpeg,gif
version = 1.0
requirements = python3,kivy,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
android.ndk = 23.2.8568313
android.sdk = 34
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.skip_update = False
android.accept_sdk_license = True
p4a.branch = develop
