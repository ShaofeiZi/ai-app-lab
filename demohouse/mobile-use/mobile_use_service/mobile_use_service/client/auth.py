import hmac
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

import requests


@dataclass
class VolcLikeSigningKey:
    secret_key: str
    region: str
    service: str
    date: str

    @property
    def scope(self) -> str:
        return f"{self.date}/{self.region}/{self.service}/request"

    @property
    def key(self) -> bytes:
        key = self.secret_key.encode("utf-8")
        for part in (self.date, self.region, self.service, "request"):
            key = hmac.new(key, part.encode("utf-8"), hashlib.sha256).digest()
        return key


class VolcLikeAuth(requests.auth.AuthBase):
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        service: str,
        session_token: str = "",
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.service = service
        self.session_token = session_token

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        now = datetime.now(timezone.utc)
        scope_date = now.strftime("%Y%m%d")
        x_date = now.strftime("%Y%m%dT%H%M%SZ")
        signing_key = VolcLikeSigningKey(
            secret_key=self.secret_key,
            region=self.region,
            service=self.service,
            date=scope_date,
        )

        body = request.body or b""
        if isinstance(body, str):
            body = body.encode("utf-8")
            request.body = body

        payload_hash = hashlib.sha256(body).hexdigest()
        request.headers["x-date"] = x_date
        request.headers["x-content-sha256"] = payload_hash
        request.headers.setdefault("Host", urlparse(request.url).netloc)
        if self.session_token:
            request.headers["x-security-token"] = self.session_token

        canonical_headers, signed_headers = self._canonical_headers(request)
        canonical_request = "\n".join(
            [
                request.method.upper(),
                self._canonical_path(request.url),
                self._canonical_query(request.url),
                canonical_headers,
                signed_headers,
                payload_hash,
            ]
        )
        string_to_sign = "\n".join(
            [
                "HMAC-SHA256",
                x_date,
                signing_key.scope,
                hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
            ]
        )
        signature = hmac.new(
            signing_key.key,
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        request.headers["Authorization"] = (
            "HMAC-SHA256 "
            f"Credential={self.access_key}/{signing_key.scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        return request

    @staticmethod
    def _canonical_path(url: str) -> str:
        path = urlparse(url).path or "/"
        if not path.startswith("/"):
            path = f"/{path}"
        return quote(path, safe="/-_.~")

    @staticmethod
    def _canonical_query(url: str) -> str:
        query = urlparse(url).query
        if not query:
            return ""
        pairs: list[tuple[str, str]] = []
        for item in query.split("&"):
            if not item:
                continue
            if "=" in item:
                key, value = item.split("=", 1)
            else:
                key, value = item, ""
            pairs.append((quote(key, safe="-_.~"), quote(value, safe="-_.~")))
        pairs.sort(key=lambda item: item[0])
        return "&".join(f"{key}={value}" for key, value in pairs)

    @staticmethod
    def _canonical_headers(request: requests.PreparedRequest) -> tuple[str, str]:
        headers: list[tuple[str, str]] = []
        for key, value in request.headers.items():
            lowered = key.lower().strip()
            if lowered in {
                "host",
                "content-type",
                "x-date",
                "x-content-sha256",
            } or lowered.startswith("x-"):
                headers.append((lowered, " ".join(str(value).split())))
        headers.sort(key=lambda item: item[0])
        canonical = "".join(f"{key}:{value}\n" for key, value in headers)
        signed = ";".join(key for key, _ in headers)
        return canonical, signed
