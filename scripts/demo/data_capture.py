"""
Data capture utility for saving API responses as test fixtures.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class DataCapture:
    """Utility for capturing API responses as test data."""
    
    def __init__(self, capture_enabled: bool = False):
        self.capture_enabled = capture_enabled
        self.sample_data_dir = Path(__file__).parent.parent.parent / "tests" / "sample_data"
        
        if self.capture_enabled:
            self.sample_data_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Data capture enabled - saving to: {self.sample_data_dir}")
    
    def _get_repo_short_name(self, repo_name: str) -> str:
        """Convert full repo name to short name for filenames."""
        name_mapping = {
            "demo-httpie-cli": "httpie-cli",
            "demo-pallets-click": "pallets-click", 
            "demo-psf-requests": "psf-requests"
        }
        return name_mapping.get(repo_name, repo_name.replace("demo-", ""))
    
    def _generate_filename(self, data_type: str, repo_name: str, timestamp: Optional[str] = None) -> str:
        """Generate filename for captured data."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        short_repo = self._get_repo_short_name(repo_name)
        return f"{data_type}_{short_repo}_{timestamp}.json"
    
    def capture_pr_status(self, pr_status: Dict[str, Any], repo_name: str) -> Optional[Path]:
        """Capture PR status data."""
        if not self.capture_enabled:
            return None
        
        filename = self._generate_filename("pr_status", repo_name)
        filepath = self.sample_data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pr_status, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Captured PR status data: {filename}")
        return filepath
    
    def capture_checks(self, checks: Dict[str, Any], repo_name: str) -> Optional[Path]:
        """Capture checks data."""
        if not self.capture_enabled:
            return None
        
        filename = self._generate_filename("checks", repo_name)
        filepath = self.sample_data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checks, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Captured checks data: {filename}")
        return filepath
    
    def capture_pr_results(self, pr_results: Dict[str, Any], repo_name: str) -> Optional[Path]:
        """Capture combined PR results data."""
        if not self.capture_enabled:
            return None
        
        filename = self._generate_filename("pr_results", repo_name)
        filepath = self.sample_data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pr_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Captured PR results data: {filename}")
        return filepath
    
    def capture_analysis_results(self, analysis: Dict[str, Any], repo_name: str) -> Optional[Path]:
        """Capture test analysis results."""
        if not self.capture_enabled:
            return None
        
        filename = self._generate_filename("analysis", repo_name)
        filepath = self.sample_data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Captured analysis results: {filename}")
        return filepath