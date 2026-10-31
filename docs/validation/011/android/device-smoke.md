# Android package verification

**Build/package verification: PASS. Device gameplay: NOT RUN (no ADB device attached).**

The release build completed through Gradle for the Meizu 20 arm64 target. APK metadata and contents were inspected locally. Installation, touch interaction, lifecycle resume, and a complete game round still require a physical Android device; no device-side result is claimed.

- APK: `dist/android/PvzMiniGame-meizu20-arm64.apk`
- Package: `com.pvzmini.doggame`
- Version: 0.6.1 (version code 1024601)
- Minimum/target Android API: 24 / 35
- ABI: arm64-v8a
- Orientation: landscape
- Size: 77,937,464 bytes.
- SHA256: `42BCCFD1EDA7811768E68A2257966C96421E43517E942F3DBCCD65757F026C9B`.

Keep task T022 open until a Meizu 20 (or equivalent supported arm64 device) completes install, launch, core touch gameplay, pause/resume, and the short animation observation.
