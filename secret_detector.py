"""
RakshakAI - Secret & Sensitive Data Leak Detector
Scans code, telemetry payloads, logs, and user reports for exposed API keys,
passwords, JWT tokens, AWS credentials, and PII (Aadhaar / Phone / Identity).
"""

import os
import re
from typing import Dict, List, Any


class SecretDetector:
    """
    Regex-based Static and Runtime Secret Scanner.
    """

    PATTERNS = {
        'OPENAI_API_KEY': re.compile(r'sk-[A-Za-z0-9-_]{32,}'),
        'GOOGLE_GEMINI_KEY': re.compile(r'AIzaSy[A-Za-z0-9-_]{33}'),
        'AWS_ACCESS_KEY': re.compile(r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'),
        'AWS_SECRET_KEY': re.compile(r'(?i)aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}'),
        'GENERIC_API_KEY': re.compile(r'(?i)(?:api_key|apikey|secret|token|auth_token)\s*[:=]\s*["\']([A-Za-z0-9-_]{16,})["\']'),
        'JWT_TOKEN': re.compile(r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+'),
        'RSA_PRIVATE_KEY': re.compile(r'-----BEGIN (?:RSA )?PRIVATE KEY-----'),
        'AADHAAR_NUMBER': re.compile(r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b'),
        'INDIAN_PHONE_NUMBER': re.compile(r'\b(?:\+91|91)?[-.\s]?[6-9]\d{9}\b')
    }

    @staticmethod
    def scan_text(text: str) -> List[Dict[str, Any]]:
        """
        Scan a string or text payload for sensitive secrets or PII.
        """
        findings = []
        if not text or not isinstance(text, str):
            return findings

        for secret_type, regex in SecretDetector.PATTERNS.items():
            for match in regex.finditer(text):
                matched_str = match.group(0)
                findings.append({
                    'type': secret_type,
                    'start': match.start(),
                    'end': match.end(),
                    'snippet': matched_str[:4] + '***' + matched_str[-3:] if len(matched_str) > 7 else '***',
                    'severity': 'CRITICAL' if 'KEY' in secret_type or 'TOKEN' in secret_type else 'MEDIUM'
                })

        return findings

    @staticmethod
    def mask_secrets(text: str) -> str:
        """
        Mask and sanitize exposed secrets from strings, logs, or error messages.
        """
        if not text or not isinstance(text, str):
            return text

        masked = text
        for secret_type, regex in SecretDetector.PATTERNS.items():
            def replace_match(match):
                val = match.group(0)
                if len(val) <= 6:
                    return f"[{secret_type}_REDACTED]"
                return f"{val[:3]}...[REDACTED_{secret_type}]...{val[-3:]}"
            masked = regex.sub(replace_match, masked)

        return masked

    @staticmethod
    def scan_file(filepath: str) -> List[Dict[str, Any]]:
        """
        Scan a single file for exposed secrets.
        """
        if not os.path.isfile(filepath):
            return []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            results = SecretDetector.scan_text(content)
            for r in results:
                r['file'] = filepath
            return results
        except Exception:
            return []

    @staticmethod
    def scan_directory(dirpath: str, exclude_dirs=None) -> List[Dict[str, Any]]:
        """
        Recursively scan a directory for exposed credentials in code or config files.
        """
        exclude_dirs = exclude_dirs or ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        all_findings = []

        for root, dirs, files in os.walk(dirpath):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.py', '.js', '.json', '.env', '.txt', '.html', '.css', '.md']:
                    filepath = os.path.join(root, file)
                    findings = SecretDetector.scan_file(filepath)
                    all_findings.extend(findings)

        return all_findings


# Global secret detector instance
secret_detector = SecretDetector()
