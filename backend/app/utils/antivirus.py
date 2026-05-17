import os
import subprocess
import hashlib
from typing import Dict, Optional
import httpx

CLAMAV_ENABLED = os.getenv("CLAMAV_ENABLED", "true").lower() == "true"
CLAMAV_SOCKET = os.getenv("CLAMAV_SOCKET", "/var/run/clamav/clamd.ctl")
VIRUSTOTAL_ENABLED = os.getenv("VIRUSTOTAL_ENABLED", "false").lower() == "true"
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

class AntivirusScanner:
    @staticmethod
    def scan_with_clamav(file_path: str) -> Dict:
        """Escanea archivo con ClamAV"""
        if not CLAMAV_ENABLED:
            return {"clean": True, "scanner": "ClamAV", "message": "ClamAV deshabilitado"}
        
        try:
            result = subprocess.run(
                ["clamdscan", "--fdpass", file_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {"clean": True, "scanner": "ClamAV", "message": "Archivo limpio"}
            elif result.returncode == 1:
                return {"clean": False, "scanner": "ClamAV", "message": "Malware detectado", "details": result.stdout}
            else:
                return {"clean": False, "scanner": "ClamAV", "message": "Error en escaneo", "details": result.stderr}
        except Exception as e:
            return {"clean": False, "scanner": "ClamAV", "message": f"Error: {str(e)}"}
    
    @staticmethod
    async def scan_with_virustotal(file_path: str) -> Dict:
        """Escanea archivo con VirusTotal (opcional)"""
        if not VIRUSTOTAL_ENABLED or not VIRUSTOTAL_API_KEY:
            return {"clean": True, "scanner": "VirusTotal", "message": "VirusTotal deshabilitado"}
        
        try:
            # Calcular hash del archivo
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            async with httpx.AsyncClient() as client:
                # Consultar hash en VirusTotal
                response = await client.get(
                    f"https://www.virustotal.com/vtapi/v2/file/report",
                    params={"apikey": VIRUSTOTAL_API_KEY, "resource": file_hash},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("response_code") == 1:
                        positives = data.get("positives", 0)
                        if positives > 0:
                            return {"clean": False, "scanner": "VirusTotal", "message": f"Detectado por {positives} motores"}
                        else:
                            return {"clean": True, "scanner": "VirusTotal", "message": "Archivo limpio"}
                    else:
                        return {"clean": True, "scanner": "VirusTotal", "message": "Archivo no encontrado en VT"}
                else:
                    return {"clean": True, "scanner": "VirusTotal", "message": "Error consultando VT"}
        except Exception as e:
            return {"clean": True, "scanner": "VirusTotal", "message": f"Error: {str(e)}"}
    
    @staticmethod
    async def scan_file(file_path: str, use_virustotal: bool = False) -> Dict:
        """Escanea archivo con ClamAV y opcionalmente VirusTotal"""
        clamav_result = AntivirusScanner.scan_with_clamav(file_path)
        
        if not clamav_result["clean"]:
            return clamav_result
        
        if use_virustotal:
            vt_result = await AntivirusScanner.scan_with_virustotal(file_path)
            if not vt_result["clean"]:
                return vt_result
        
        return {"clean": True, "scanner": "ClamAV", "message": "Archivo seguro"}
