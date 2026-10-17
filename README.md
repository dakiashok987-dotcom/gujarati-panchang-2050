# ગુજરાતી પંચાંગ 2050
Build (needs Node 18+, JDK 17, Android Studio/SDK):
  npm install && npx cap add android && npx cap sync android
  cd android && ./gradlew assembleDebug
APK: android/app/build/outputs/apk/debug/app-debug.apk
If missing, add to android/app/src/main/AndroidManifest.xml:
  <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
Lunar festivals: fill "lunar" in www/festivals.json: {"d":"YYYY-MM-DD","n":"નામ","v":true,"tithi":"","paksha":"","nak":""}

## તહેવાર ડેટા 2026–2035 (ઉમેરાયો)
- `www/festivals.json` (version 3): જૂના `fixed` અખંડ; `lunar` માં 2026–2035 ના તહેવારો ઉમેર્યા. બધી ચંદ્ર-તારીખો ગણતરી આધારિત છે (`v:false` = "ચકાસણી બાકી"). છાપેલા ગુજરાતી પંચાંગથી મેળવ્યા પછી જ `v:true` કરો.
- ફરી બનાવવા: `python3 tools/gen.py && python3 tools/merge.py` (વધારાના ફીલ્ડ id, category, cats, tradition, major, source — જૂનો કોડ તેમને અવગણે છે).
- version 2 થી 3 કર્યું જેથી ફોનમાં સંગ્રહાયેલ જૂનો કેશ નવા ડેટાને ઢાંકી ન દે.


## નોંધ: તારીખોની ચકાસણી
- `festivals.json` માં ચંદ્ર-તિથિ આધારિત તમામ તારીખો `v:false` રાખવામાં આવી છે; એટલે એપમાં તે “ચકાસણી બાકી” તરીકે દેખાવું જોઈએ.
- 2026 હોળી શ્રેણીમાં ઉપલબ્ધ ગુજરાતી પંચાંગ વેબ-સંદર્ભ સાથે મેળ બેસાડવા માટે હોળિકા દહન 3 માર્ચ અને હોળી/ધુળેટી 4 માર્ચ દર્શાવ્યાં છે. અન્ય વર્ષોની તારીખો હજી સ્વતંત્ર રીતે ચકાસેલી નથી.
- કૃપા કરીને આ ડેટાને સત્તાવાર ધાર્મિક/જાહેર રજાના નિશ્ચિત રેકોર્ડ તરીકે ઉપયોગ કરતાં પહેલાં સ્થાનિક પંચાંગ સાથે ચકાસો.
