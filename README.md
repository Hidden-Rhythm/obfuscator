 <div align="center">

# 🔐 obfuscator

### Multi-Layer Python Source Code Obfuscation

*Transform Python source into a layered, obfuscated output through a terminal-based workflow.*

<br>

<a href="https://github.com/Hidden-Rhythm/obfuscator">
  <img src="https://img.shields.io/badge/💻_Source-GitHub-18181b?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Source">
</a>
<img src="https://img.shields.io/badge/🐍_Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
<img src="https://img.shields.io/badge/Version-1.0.0-52525b?style=for-the-badge" alt="Version 1.0.0">

<br><br>

**AST TRANSFORMATION** &nbsp;·&nbsp; **PAYLOAD ENCODING** &nbsp;·&nbsp; **LAYERED LOADING**

</div>

---

## 🚀 The Next Version Is Coming Soon

<div align="center">

### A New Level of Python Obfuscation

**Version 2.0 is in development.**

The next release is being planned with a focus on stronger obfuscation, more sophisticated code transformations, and improvements to the overall processing pipeline.

</div>

The goal is to take the current obfuscation workflow further while continuing to refine the developer experience.

- 🔒 **Improved Obfuscation** — planned enhancements to make transformed source code harder to inspect.
- 🧬 **Advanced Transformations** — further development of the code transformation pipeline.
- ⚙️ **Pipeline Improvements** — continued refinement of the generation and processing workflow.

<sub>These are development goals, not features available in the current release. Details may change as development progresses.</sub>

**Stay tuned for the next release.** ⚡

---

## 🧩 What Is obfuscator?

**obfuscator** is a Python utility designed to make source code harder to inspect by transforming selected parts of a program and generating a layered output file.

Rather than relying only on variable renaming or whitespace removal, it combines multiple techniques, including abstract syntax tree (AST) transformations, encoded constants, compiled bytecode serialization, compression, and generated loader stages.

The application is built around a terminal interface powered by [Rich](https://github.com/Textualize/rich), providing a live processing dashboard with progress indicators, execution logs, stage timings, and output metrics.

> 🎯 **The goal:** provide a self-contained Python obfuscation workflow with detailed build feedback and a generated output file.

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **AST Transformation** | Parses Python source code and transforms eligible syntax-tree nodes. |
| 🔒 **Constant Encoding** | Applies XOR-based encoding to eligible string and byte constants. |
| 📦 **Payload Compression** | Compiles transformed code, serializes its code object, and compresses the resulting payload. |
| 🧬 **Layered Loader** | Generates bootstrap and runtime-loading stages for the transformed payload. |
| 🔤 **Dynamic Imports** | Rewrites supported import statements into dynamic import calls. |
| 🎲 **Generated Identifiers** | Creates varying identifiers and additional generated code structures. |
| 🖥️ **Live Terminal UI** | Displays processing stages, progress, logs, and build information. |
| ✅ **Syntax Verification** | Checks the generated source for syntax errors before writing the output. |
| 🔍 **Build Metrics** | Reports file sizes, stage timings, and the generated file's SHA-256 hash. |
| 📄 **Single-File Application** | Keeps the main application in `obfuscator.py`. |

## ⚙️ How It Works

The application organizes processing into eight stages.

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

Each stage contributes to the final output. The terminal dashboard tracks progress and displays relevant metrics throughout the process.

## 🖥️ Terminal Dashboard

The application uses Rich to present a live-updating terminal dashboard instead of a sequence of plain print statements.

The interface includes:

- 📊 Current processing stage and progress
- 📝 Build logs and status information
- ⏱️ Per-stage timing information
- 📏 Source, payload, intermediate, and output sizes
- 🔑 SHA-256 hash of the generated output
- ⚠️ Error reporting when processing fails

The dashboard also supports cancellation using `Ctrl+C`.

## 🚀 Getting Started

### 📋 Requirements

- Python **3.10 or later** recommended
- `pip` for installing Python packages
- An existing Python source file to process

The terminal interface uses the Rich library. If the import is unavailable, the script attempts to install or upgrade Rich automatically, so an internet connection and permission to install packages may be required on first launch.

### 1. Clone the Repository

```bash
git clone https://github.com/Hidden-Rhythm/obfuscator.git
cd obfuscator
```

### 2. Install the Dependency

```bash
python -m pip install rich
```

### 3. Launch the Application

```bash
python obfuscator.py
```

When prompted, provide the path to the Python file you want to process.

## 📂 Input & Output

The application accepts an existing Python source file and prompts for an output path, with a default filename based on the original file.

**Example input**

```text
example.py
```

**Default output**

```text
example_obf.py
```

The generated file contains the transformed program and its generated loading code.

> 💡 Always keep an untouched copy of your original source before processing it.

## 🧪 VirusTotal Scan Results

<div align="center">

### 🛡️ 0 Detections

**Observed result during testing**

</div>

The generated Python file returned **0 detections on VirusTotal** in the scan performed during testing.

This result describes only that particular scan. Detection results may differ across files, security engines, and scan dates. A zero-detection result does not prove that a file is safe, establish that it is undetectable, or guarantee future scan results.

## 🔬 Technical Details

| Component | Implementation |
|---|---|
| Source parsing | Python `ast` |
| Constant encoding | XOR-based transformation |
| Payload serialization | `marshal` |
| Compression | `zlib` |
| Payload representation | Base64 chunks |
| Hashing and stream generation | `hashlib` |
| Terminal interface | `rich` |
| Output verification | Python syntax compilation |
| Build fingerprint | SHA-256 |

### ⚠️ Compatibility & Limitations

- **Python versions:** The generated payload uses `marshal`-serialized code objects, which are Python-version-dependent. Generate and run output in a compatible environment.
- **Program behavior:** Rewriting imports and transforming constants may affect programs that rely on particular import semantics, runtime inspection, or advanced language features.
- **Unchanged constructs:** Some constructs, including f-strings, are deliberately left outside the constant transformation.
- **Runtime checks:** The generated loader contains environment and timing checks that can affect execution in some environments.
- **Security:** Obfuscation increases the effort needed to inspect code, but it is not a substitute for encryption, secure key management, or access controls.

Test generated output thoroughly before using it in a production workflow.

## 🗂️ Project Structure

```text
obfuscator/
└── obfuscator.py
```

The main application, processing pipeline, and terminal interface are contained in `obfuscator.py`.

## 🛠️ Built With

| Technology | Purpose |
|---|---|
| 🐍 Python | Core application and transformation pipeline |
| 🧠 AST | Source-code parsing and transformations |
| 📦 `marshal` | Code-object serialization |
| 🗜️ `zlib` | Payload compression |
| 🔑 `hashlib` | Hashing and keystream generation |
| 🎨 Rich | Terminal dashboard, panels, tables, and progress display |

## 🔗 Links

<div align="center">

<a href="https://github.com/Hidden-Rhythm/obfuscator">
  <img src="https://img.shields.io/badge/Repository-View%20Source-18181b?style=for-the-badge&logo=github&logoColor=white" alt="View Repository">
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

### ⚡ Built with Python.

**Hidden-Rhythm**

<sub>obfuscator · v1.0.0 · Next version in development</sub>

</div>
