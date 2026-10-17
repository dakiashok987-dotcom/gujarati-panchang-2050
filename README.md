# ગુજરાતી પંચાંગ 2050
Build (needs Node 18+, JDK 17, Android Studio/SDK):
  npm install && npx cap add android && npx cap sync android
  cd android && ./gradlew assembleDebug
APK: android/app/build/outputs/apk/debug/app-debug.apk
If missing, add to android/app/src/main/AndroidManifest.xml:
  <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
Lunar festivals: fill "lunar" in www/festivals.json: {"d":"YYYY-MM-DD","n":"નામ","v":true,"tithi":"","paksha":"","nak":""}
