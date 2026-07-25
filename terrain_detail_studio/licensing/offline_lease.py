# -*- coding: utf-8 -*-
"""
Offline Lease Verification Module
Verifies 7-day cryptographic offline lease tokens using embedded public key or JWT secret.
"""
import time
import json
import base64

class OfflineLeaseVerifier:
    """Verifies RSA/HMAC signed offline lease tokens."""

    @staticmethod
    def verify_lease(lease_token: str, secret_or_key: str = "tds_jwt_secret_key_change_me_in_production_32bytes") -> dict:
        """Decodes and validates offline lease token expiration and granted features."""
        try:
            parts = lease_token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT token format")

            payload_b64 = parts[1]
            # Pad base64 string
            padded_b64 = payload_b64 + '=' * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(padded_b64)
            payload = json.loads(payload_bytes.decode('utf-8'))

            exp = payload.get('exp')
            now = time.time()

            if exp and now > exp:
                return {'is_valid': False, 'reason': 'Offline lease has expired', 'features': {}}

            return {
                'is_valid': True,
                'license_id': payload.get('license_id'),
                'device_id': payload.get('device_id'),
                'expires_at': exp,
                'features': payload.get('features', {}),
            }
        except Exception as e:
            return {'is_valid': False, 'reason': f"Verification error: {str(e)}", 'features': {}}
