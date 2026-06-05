# 🧠 Scythez – Ultimate SQL/NoSQL Injection Framework

**Scythez** (formerly ParamSQL v5.0) is a high‑performance, fully automated penetration testing tool designed to discover and exploit **SQL Injection** and **NoSQL Injection** vulnerabilities. It features intelligent WAF bypass, automatic session management, multi‑protocol support (GET/POST/PUT/DELETE/PATCH), and seamless database extraction.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Status](https://img.shields.io/badge/status-stable-brightgreen)

![Scythez Banner](https://raw.githubusercontent.com/sigmaboysigmaboy888-prog/Scythez/refs/heads/main/foto.png)

---

## 🚀 Features

- **15,000+ Payloads** – Time‑based, Boolean, Error, Union, Stacked, Blind, OOB, Second‑Order, NoSQL.
- **WAF Bypass** – Automatic payload mutation (case randomisation, comment injection, URL encoding, hex, null byte, etc.)
- **Auto DBMS Fingerprint** – MySQL, MSSQL, PostgreSQL, Oracle, SQLite.
- **NoSQL Injection** – MongoDB & CouchDB (`$ne`, `$gt`, `$regex`, `$where`).
- **Multi‑Protocol** – GET, POST, PUT, DELETE, PATCH with JSON / XML / form‑urlencoded bodies.
- **Session & Cookie Automation** – Load/save cookies, auto‑capture from responses, reuse for authenticated scans.
- **Auto Database Dump** (`--cd`) – Steal cookies and extract tables, columns, user data without manual credentials.
- **Zero CPU Heat** – Optimised threading (150 threads, small delay) – runs smoothly on any machine.
- **Batch Scanning** – Scan multiple targets from a file (`--batch targets.txt`).
- **Tor Proxy Support** – Anonymise requests via `--tor`.

---

## 📦 Installation

```bash
git clone https://github.com/scythez/scythez.git
cd scythez
pip install -r requirements.txt
chmod +x start.sh
scythez
