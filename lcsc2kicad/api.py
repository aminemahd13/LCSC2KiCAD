"""
API client for fetching component data from LCSC/EasyEDA
"""

import logging
import requests
from typing import Optional, Dict

from lcsc2kicad import __version__

# API Endpoints
API_ENDPOINT = "https://easyeda.com/api/products/{lcsc_id}/components?version=6.4.19.5"
ENDPOINT_3D_MODEL = "https://modules.easyeda.com/3dmodel/{uuid}"
ENDPOINT_3D_MODEL_STEP = "https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/{uuid}"


class LCSCApi:
    """Client for LCSC/EasyEDA API"""
    
    def __init__(self):
        self.headers = {
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": f"lcsc2kicad v{__version__}",
        }
    
    def get_component_info(self, lcsc_id: str) -> Optional[Dict]:
        """
        Fetch component information from API
        
        Args:
            lcsc_id: LCSC part number (e.g., C2040)
            
        Returns:
            Component data dictionary or None if failed
        """
        try:
            logging.info(f"Fetching component info for {lcsc_id}")
            url = API_ENDPOINT.format(lcsc_id=lcsc_id)
            response = requests.get(url=url, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                logging.error(f"API request failed with status {response.status_code}")
                return None
            
            api_response = response.json()
            
            if not api_response or (
                "code" in api_response and api_response.get("success") is False
            ):
                logging.error(f"API returned error: {api_response}")
                return None
            
            logging.info(f"Successfully fetched data for {lcsc_id}")
            return api_response
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error fetching component: {e}")
            return None
        except Exception as e:
            logging.error(f"Error fetching component info: {e}")
            return None
    
    def get_cad_data(self, lcsc_id: str) -> Optional[Dict]:
        """
        Get CAD data (symbol, footprint, 3D model) for component
        
        Args:
            lcsc_id: LCSC part number
            
        Returns:
            CAD data dictionary or None if failed
        """
        component_info = self.get_component_info(lcsc_id)
        
        if not component_info:
            return None
        
        if "result" not in component_info:
            logging.error("No CAD data in API response")
            return None
        
        return component_info["result"]
    
    def get_3d_model_obj(self, uuid: str) -> Optional[str]:
        """
        Download raw 3D model in OBJ format
        
        Args:
            uuid: 3D model UUID
            
        Returns:
            Model data as string or None if failed
        """
        try:
            url = ENDPOINT_3D_MODEL.format(uuid=uuid)
            response = requests.get(
                url=url,
                headers={"User-Agent": self.headers["User-Agent"]},
                timeout=30
            )
            
            if response.status_code != 200:
                logging.error(f"Failed to download 3D model OBJ for {uuid}")
                return None
            
            return response.content.decode()
            
        except Exception as e:
            logging.error(f"Error downloading 3D model OBJ: {e}")
            return None
    
    def get_3d_model_step(self, uuid: str) -> Optional[bytes]:
        """
        Download 3D model in STEP format
        
        Args:
            uuid: 3D model UUID
            
        Returns:
            Model data as bytes or None if failed
        """
        try:
            url = ENDPOINT_3D_MODEL_STEP.format(uuid=uuid)
            response = requests.get(
                url=url,
                headers={"User-Agent": self.headers["User-Agent"]},
                timeout=30
            )
            
            if response.status_code != 200:
                logging.error(f"Failed to download 3D model STEP for {uuid}")
                return None
            
            return response.content
            
        except Exception as e:
            logging.error(f"Error downloading 3D model STEP: {e}")
            return None
