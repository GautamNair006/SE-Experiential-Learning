# Issues Identified During Static Analysis

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|-------------|
| Use of weak MD5 hash | Security | 47 | MD5 is a weak hashing algorithm and was flagged by Bandit (B324). | Replaced `hashlib.md5()` with `hashlib.sha256()`. |
| Use of eval() | Security | 42 | `eval()` can execute arbitrary code and was flagged by Bandit (B307). | Replaced with direct fine calculation logic. |
| os.system() usage | Security | 58 | `os.system()` may allow command injection and was flagged by Bandit (B605). | Replaced with a simple `print()` statement. |
| Insecure random generator | Security | 51 | `random.randint()` is unsuitable for generating security-sensitive PINs. | Replaced with `secrets.randbelow()`. |
| Mutable default argument | Bug | 14 | Default list argument could be shared across function calls. | Changed default parameter to `None` and initialized inside the function. |
| Missing function docstrings | Code Quality | Multiple | Functions lacked documentation and reduced code readability. | Added docstrings to all functions. |
| Non-snake-case function name | Style | 14 | `issueBook` violated Python naming conventions. | Renamed to `issue_book`. |
| Missing encoding and context manager | Code Quality | 53-55 | File opened without specifying encoding and not using a context manager. | Replaced with `with open(..., encoding="utf-8")`. |
