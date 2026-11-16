"""Lightweight Supabase REST client helper for Pag-Laum using Python's standard library."""

import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings


def is_supabase_configured() -> bool:
    """Return True when both SUPABASE_URL and SUPABASE_ANON_KEY are configured."""
    return bool(getattr(settings, "SUPABASE_URL", "") and getattr(settings, "SUPABASE_ANON_KEY", ""))


def get_supabase_headers(api_key: str | None = None) -> dict[str, str]:
    """Build standard Supabase REST API request headers."""
    key = api_key if api_key is not None else getattr(settings, "SUPABASE_ANON_KEY", "")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def build_rest_url(table_name: str, query_params: dict[str, str] | None = None) -> str:
    """Construct a Supabase PostgREST endpoint URL for a table."""
    base_url = getattr(settings, "SUPABASE_URL", "").rstrip("/")
    clean_table = table_name.lstrip("/")
    url = f"{base_url}/rest/v1/{clean_table}" if clean_table else f"{base_url}/rest/v1/"
    if query_params:
        url = f"{url}?{urllib.parse.urlencode(query_params)}"
    return url


def fetch_table(table_name: str, select: str = "*", timeout: float = 3.0) -> list[dict] | None:
    """Fetch rows from a Supabase REST table, returning None if unconfigured or unreachable."""
    if not is_supabase_configured():
        return None

    url = build_rest_url(table_name, {"select": select})
    request = urllib.request.Request(url, headers=get_supabase_headers(), method="GET")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                return None
            payload = json.loads(response.read().decode("utf-8"))
            return payload if isinstance(payload, list) else None
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def probe_supabase_endpoint(timeout: float = 3.0) -> dict:
    """Probe the configured Supabase REST endpoint and report reachability and status code."""
    url = build_rest_url("")
    headers = get_supabase_headers() if is_supabase_configured() else {"Accept": "application/json"}
    request = urllib.request.Request(url, headers=headers, method="GET")

    result = {
        "url": getattr(settings, "SUPABASE_URL", ""),
        "project_ref": getattr(settings, "SUPABASE_PROJECT_REF", ""),
        "has_key": is_supabase_configured(),
        "reachable": False,
        "status_code": None,
    }

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result["reachable"] = True
            result["status_code"] = response.status
    except urllib.error.HTTPError as exc:
        result["reachable"] = True
        result["status_code"] = exc.code
    except (urllib.error.URLError, TimeoutError) as exc:
        result["error"] = str(exc)

    return result
