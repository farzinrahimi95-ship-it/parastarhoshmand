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
android.skip_update = True
android.accept_sdk_license = True
android.ndk = 25.2.9519653
android.sdk = 33
p4a.branch = develop
android.build_mode = debug
p4a.branch = develop
android.sdk = 33
android.ndk = 25.2.9519653
android.skip_update = False
