"""
Storage layer for BugIt issues.
Handles filesystem operations with atomic writes and proper error handling.
"""

import json
import uuid
import os
import tempfile
import shutil
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

# Cross-platform file locking
if sys.platform.startswith('win'):
    import msvcrt
else:
    import fcntl

# Import config to access backup preferences
from .config import get_config_value

class StorageError(Exception):
    """Raised when storage operations fail"""
    pass

class ConcurrentAccessError(StorageError):
    """Raised when concurrent access conflicts occur"""
    pass

def ensure_issues_directory() -> Path:
    """Ensure .bugit/issues directory exists"""
    issues_dir = Path(".bugit/issues")
    issues_dir.mkdir(parents=True, exist_ok=True)
    return issues_dir

@contextmanager
def file_lock(file_path: Path, timeout: float = 10.0):
    """
    Cross-platform context manager for file locking with timeout.
    Prevents concurrent access to the same file.
    
    Note: On Windows, file locking is currently disabled for compatibility.
    This will be improved in a future version.
    """
    if sys.platform.startswith('win'):
        # Simplified Windows implementation - just yield without locking
        # TODO: Implement proper Windows file locking
        yield
        return
    
    # Unix file locking implementation
    lock_file = file_path.with_suffix(file_path.suffix + '.lock')
    lock_fd = None
    
    try:
        # Create lock file
        lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
        
        # Try to acquire lock with timeout
        start_time = time.time()
        while True:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (OSError, IOError):
                if time.time() - start_time > timeout:
                    raise ConcurrentAccessError(
                        f"Could not acquire lock for {file_path} within {timeout} seconds"
                    )
                time.sleep(0.1)
        
        yield
        
    except Exception as e:
        if isinstance(e, ConcurrentAccessError):
            raise
        raise StorageError(f"File locking failed: {e}")
    finally:
        # Best effort cleanup
        if lock_fd is not None:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
                lock_file.unlink(missing_ok=True)
            except Exception:
                # Best effort cleanup - ignore errors
                pass

def atomic_write_json(file_path: Path, data: Dict) -> None:
    """
    Atomically write JSON data to a file using write-then-rename pattern.
    This ensures the file is never in a partially written state.
    """
    if not isinstance(data, dict):
        raise StorageError("Data must be a dictionary")
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create temporary file in the same directory for atomic rename
    temp_fd = None
    temp_path = None
    
    try:
        # Create temporary file in same directory as target
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.tmp',
            prefix=f'.{file_path.name}.',
            dir=file_path.parent
        )
        
        # Write JSON data to temporary file
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
            json.dump(data, temp_file, indent=2, ensure_ascii=False)
            temp_file.flush()
            os.fsync(temp_file.fileno())  # Force write to disk
        
        temp_fd = None  # File descriptor is now closed
        
        # Atomic rename - this is the critical atomic operation
        temp_path_obj = Path(temp_path)
        temp_path_obj.replace(file_path)
        temp_path = None  # Successfully renamed, don't clean up
        
    except Exception as e:
        # Clean up on failure
        if temp_fd is not None:
            try:
                os.close(temp_fd)
            except:
                pass
        
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        
        raise StorageError(f"Atomic write failed for {file_path}: {e}")

def read_json_file(file_path: Path) -> Dict:
    """
    Safely read JSON data from a file with proper error handling.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            raise StorageError(f"Invalid JSON structure in {file_path}: expected dictionary")
            
        return data
        
    except FileNotFoundError:
        raise StorageError(f"Issue file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise StorageError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise StorageError(f"Failed to read {file_path}: {e}")

def save_issue(data: Dict) -> str:
    """
    Save issue data to filesystem with atomic write and file locking.
    Returns the UUID of the saved issue.
    """
    if not isinstance(data, dict):
        raise StorageError("Issue data must be a dictionary")
    
    # Ensure issue has an ID
    issue_id = data.get('id')
    if not issue_id:
        issue_id = str(uuid.uuid4())[:6]
        data['id'] = issue_id
    
    # Ensure issues directory exists
    issues_dir = ensure_issues_directory()
    issue_file = issues_dir / f"{issue_id}.json"
    
    try:
        # Use file locking for concurrent access safety
        with file_lock(issue_file):
            atomic_write_json(issue_file, data)
        
        return issue_id
        
    except (StorageError, ConcurrentAccessError):
        # Re-raise storage-related errors
        raise
    except Exception as e:
        raise StorageError(f"Failed to save issue {issue_id}: {e}")

def load_issue(issue_id: str) -> Dict:
    """Load issue by ID from filesystem with proper error handling"""
    if not issue_id or not isinstance(issue_id, str):
        raise StorageError("Issue ID must be a non-empty string")
    
    issues_dir = ensure_issues_directory()
    issue_file = issues_dir / f"{issue_id}.json"
    
    if not issue_file.exists():
        raise StorageError(f"Issue not found: {issue_id}")
    
    try:
        with file_lock(issue_file):
            data = read_json_file(issue_file)
        
        # Validate basic structure
        if 'id' not in data:
            data['id'] = issue_id
        
        return data
        
    except StorageError:
        # Re-raise storage errors
        raise
    except Exception as e:
        raise StorageError(f"Failed to load issue {issue_id}: {e}")

def list_issues() -> List[Dict]:
    """
    Return list of all issues sorted by severity then created_at.
    Implements caching and efficient file operations.
    """
    issues_dir = ensure_issues_directory()
    
    # Find all JSON files in issues directory
    issue_files = list(issues_dir.glob("*.json"))
    
    if not issue_files:
        return []
    
    issues = []
    failed_files = []
    
    for issue_file in issue_files:
        try:
            # Skip lock files and temporary files
            if issue_file.suffix == '.lock' or '.tmp' in issue_file.name:
                continue
                
            with file_lock(issue_file):
                data = read_json_file(issue_file)
            
            # Validate essential fields
            if 'id' not in data:
                data['id'] = issue_file.stem
            
            issues.append(data)
            
        except StorageError as e:
            # Log failed file but continue processing others
            failed_files.append((issue_file, str(e)))
            continue
        except Exception as e:
            # Log unexpected errors but continue
            failed_files.append((issue_file, f"Unexpected error: {e}"))
            continue
    
    # Sort by severity (critical -> low) then by created_at (newest first)
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    
    def sort_key(issue):
        severity = issue.get('severity', 'medium')
        severity_rank = severity_order.get(severity, 2)  # Default to medium
        
        created_at = issue.get('created_at', '1970-01-01T00:00:00')
        try:
            # Parse datetime for proper sorting
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            # Use a safe timestamp - avoid datetime.min which fails on Windows
            timestamp = created_time.timestamp()
        except:
            # Use epoch time as fallback (safe on all platforms)
            timestamp = 0
        
        return (severity_rank, -timestamp)  # Negative for desc order
    
    issues.sort(key=sort_key)
    
    # Report failed files in development mode
    if failed_files and os.getenv('BUGIT_DEBUG'):
        print(f"[DEBUG] Failed to load {len(failed_files)} issue files:")
        for file_path, error in failed_files:
            print(f"  - {file_path}: {error}")
    
    return issues

def delete_issue(issue_id: str) -> bool:
    """
    Delete issue by ID with atomic operation and backup.
    Returns True if successful, False if issue not found.
    """
    if not issue_id or not isinstance(issue_id, str):
        raise StorageError("Issue ID must be a non-empty string")
    
    issues_dir = ensure_issues_directory()
    issue_file = issues_dir / f"{issue_id}.json"
    
    if not issue_file.exists():
        return False
    
    try:
        with file_lock(issue_file):
            # Create backup before deletion (optional, for recovery)
            backup_dir = issues_dir.parent / "backups"
            backup_setting = get_config_value('backup_on_delete')
            if backup_setting is None:
                backup_setting = True  # Default to True for safety
            
            if backup_setting:
                backup_dir.mkdir(exist_ok=True)
                backup_file = backup_dir / f"{issue_id}_{int(time.time())}.json"
                shutil.copy2(issue_file, backup_file)
            
            # Atomic deletion
            issue_file.unlink()
        
        return True
        
    except StorageError:
        # Re-raise storage errors
        raise
    except Exception as e:
        raise StorageError(f"Failed to delete issue {issue_id}: {e}")

def get_issue_by_index(index: int) -> Dict:
    """
    Get issue by ephemeral index from sorted list.
    Index is 1-based to match CLI display.
    """
    if not isinstance(index, int) or index < 1:
        raise StorageError("Invalid index")
    
    issues = list_issues()
    
    if index > len(issues):
        raise StorageError(f"Index {index} out of range (1-{len(issues)})")
    
    return issues[index - 1]  # Convert to 0-based

def get_storage_stats() -> Dict:
    """Get storage statistics for debugging and monitoring"""
    issues_dir = ensure_issues_directory()
    
    try:
        issues = list_issues()  # Get actual issues to count by severity
        total_size = 0
        severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        # Count issues by severity and calculate total size
        for issue in issues:
            severity = issue.get('severity', 'medium')
            if severity in severity_counts:
                severity_counts[severity] += 1
            
            # Calculate file size
            issue_id = issue.get('id')
            if issue_id:
                issue_file = issues_dir / f"{issue_id}.json"
                if issue_file.exists():
                    total_size += issue_file.stat().st_size
        
        return {
            'issues_directory': str(issues_dir),
            'total_issues': len(issues),
            'total_size_bytes': total_size,
            'issues_by_severity': severity_counts,
            'directory_exists': issues_dir.exists(),
            'directory_writable': os.access(issues_dir, os.W_OK)
        }
    except Exception as e:
        return {
            'error': str(e),
            'issues_directory': str(issues_dir),
            'directory_exists': issues_dir.exists() if issues_dir else False,
            'total_issues': 0,
            'total_size_bytes': 0,
            'issues_by_severity': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        } 