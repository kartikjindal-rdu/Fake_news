
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional

router = APIRouter()

# In-memory history store.
# Only actual scans should be added by the analysis workflow.
SCAN_STORE: List[Dict[str, Any]] = []

MAX_HISTORY = 100


def add_scan(scan_dict: Dict[str, Any]) -> None:
    """Append a completed scan result to the in-memory history."""
    SCAN_STORE.insert(0, scan_dict)
    # Prevent unbounded growth.
    while len(SCAN_STORE) > MAX_HISTORY:
        SCAN_STORE.pop()


def get_scan_by_id(scan_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single scan from memory by its ID, or None if not found."""
    for scan in SCAN_STORE:
        if scan.get("scanId") == scan_id:
            return scan
    return None



@router.get("", response_model=List[Dict[str, Any]])
def get_all_scans():
    """Return scans recorded during the current backend process."""
    return SCAN_STORE


@router.get("/{scan_id}", response_model=Dict[str, Any])
def get_scan(scan_id: str):
    """Retrieve a single scan from the in-memory history by its ID."""
    for scan in SCAN_STORE:
        if scan.get("scanId") == scan_id:
            return scan

    raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found.")


@router.delete("/{scan_id}")
def delete_scan(scan_id: str):
    """Delete a scan from the in-memory history."""
    for index, scan in enumerate(SCAN_STORE):
        if scan.get("scanId") == scan_id:
            del SCAN_STORE[index]
            return {
                "status": "success",
                "deleted": scan_id,
            }

    return {
        "status": "not_found",
        "deleted": None,
        "message": "No scan with that ID exists in the current history.",
    }
