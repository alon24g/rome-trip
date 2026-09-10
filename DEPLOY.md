# Rome Trip — build / test / deploy

Project files:

```
index.html      the app (itinerary + map + checklist)
                every day has a lunch + dinner stop; every stop has a
                "where to eat" line and a vegan note
manifest.json   PWA manifest (name, colors, icons)
sw.js           service worker — same-origin cache, network-first page loads
vendor/leaflet/ Leaflet 1.9.4 (js/css/images) bundled locally — no CDN
icons/          icon-180 / 192 / 512 .png (terracotta Colosseum)
tools/make_icons.py   regenerates the icons (pure Python, no deps)
```

---

## 1. Test locally on your computer

From this folder (`C:\Users\USER\Projects\project_1`):

```powershell
py -m http.server 8080
```

Open <http://localhost:8080> in Chrome. Then check DevTools (F12):
- **Application → Manifest** — no errors, icons show.
- **Application → Service Workers** — `sw.js` is "activated and running".
- Tick **Offline** in the Service Workers panel, reload — the app still loads
  (map tiles go blank, everything else works).

Stop the server with `Ctrl+C`.

### If the page or map looks stale / broken after an update

A previously-installed service worker can keep serving an old cached copy.
One-time fix: DevTools (F12) → **Application** → **Storage** →
**Clear site data**, then reload. Or just test on a fresh port
(`py -m http.server 8090`) — a new port is a clean slate with no old cache.
After this the app self-updates: a new version reloads the page once on its own.

## 2. Test on your phone over the same Wi-Fi

Find your computer's LAN IP:

```powershell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like '192.168.*' -or $_.IPAddress -like '10.*' }).IPAddress
```

Say it prints `192.168.1.42`. Keep the server running, and on your phone
(same Wi-Fi) open:

```
http://192.168.1.42:8080
```

- **iPhone (Safari):** Share → *Add to Home Screen*.
- **Android (Chrome):** ⋮ menu → *Add to Home screen* / *Install app*.

> Note: over plain `http://` on a LAN IP the service worker will NOT register
> (browsers require HTTPS or `localhost` for that). "Add to Home Screen" still
> works for testing the icon/name/standalone window. Full offline caching kicks
> in once it's on an HTTPS URL — that's step 3.

## 3. Deploy to a permanent free HTTPS URL

### Option A — GitHub Pages (terminal, stable URL, recommended)

1. Create an empty repo at <https://github.com/new> named `rome-trip`
   (no README, no .gitignore).
2. In this folder:

   ```powershell
   git init
   git add .
   git commit -m "Rome Trip PWA"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/rome-trip.git
   git push -u origin main
   ```

   The first `push` opens a browser window to sign in to GitHub
   (Git for Windows ships the credential manager — no token to paste manually).
3. Repo → **Settings → Pages** → *Source: Deploy from a branch* →
   Branch **main**, folder **/ (root)** → **Save**.
4. Wait ~1 minute. Your app is at:

   ```
   https://YOUR_USERNAME.github.io/rome-trip/
   ```

   Open that on your phone → Add to Home Screen. Done. Works offline anywhere
   after the first load.

To update later: `git add . && git commit -m "update" && git push` — Pages
redeploys automatically. Bump the `CACHE` version in `sw.js`
(`rome-trip-v3` -> `-v4` -> ...) whenever you change files. The app also
reloads itself once when a new version is detected, so phones don't get stuck
on an old copy.

### Option B — Netlify Drop (no account setup, no git)

Go to <https://app.netlify.com/drop> and drag this whole folder onto the page.
You get an instant `https://<random-name>.netlify.app` URL (free, HTTPS,
renameable in Site settings). Simplest if you don't want to touch git.

## 4. (Optional) Native app wrapper

Skip Capacitor — it needs Node.js + Android Studio (APK) or a Mac + Xcode (iOS)
set up locally, which is a lot for the payoff here.

Easier: once step 3 is live, go to <https://www.pwabuilder.com>, paste your
URL, and it packages a signed **Android APK / .aab** and an **iOS project**
straight from the manifest + service worker already in this project. The
installable PWA from step 3 is the real deliverable, though — this is just a
bonus if you want a store build.
