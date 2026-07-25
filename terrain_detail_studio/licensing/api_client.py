# -*- coding: utf-8 -*-
"""
API Client Module for QGIS Plugin
Communicates with Vercel API Gateway endpoints.
"""
import urllib.request
import urllib.parse
import json

class PluginAPIClient:
    """Client for communicating with Terrain Detail Studio Backend API."""

    def __init__(self, api_base: str = "http://localhost:3000/v1"):
        self.api_base = api_base.rstrip('/')

    def get_entitlements(self, access_token: str) -> dict:
        """Fetches active entitlement JSON."""
        url = f"{self.api_base}/entitlements"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            raise RuntimeError(f"Failed to fetch entitlements: {e}")

    def issue_offline_lease(self, access_token: str) -> dict:
        """Requests signed 7-day offline lease token."""
        url = f"{self.api_base}/offline-leases/issue"
        req = urllib.request.Request(url, method='POST', headers={'Authorization': f'Bearer {access_token}'})
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            raise RuntimeError(f"Failed to issue offline lease: {e}")
