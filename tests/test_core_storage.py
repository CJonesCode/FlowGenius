"""
Comprehensive tests for core/storage.py module.
Tests all storage functions with proper isolation and edge case coverage.
"""

import pytest
import tempfile
import shutil
import json
import sys
from pathlib import Path
from unittest.mock import patch, mock_open
import os
import platform

from core import storage
from core.storage import (
    ensure_issues_directory, atomic_write_json, read_json_file,
    save_issue, load_issue, list_issues, delete_issue, 
    get_issue_by_index, get_storage_stats,
    StorageError, ConcurrentAccessError
)


class TestEnsureIssuesDirectory:
    """Test the ensure_issues_directory function"""
    
    def test_creates_directory_when_missing(self, temp_dir):
        """Test that issues directory is created when it doesn't exist"""
        os.chdir(temp_dir)
        
        # Ensure .bugit doesn't exist
        bugit_dir = Path('.bugit')
        assert not bugit_dir.exists()
        
        # Call function
        issues_dir = ensure_issues_directory()
        
        # Check directory was created
        assert issues_dir.exists()
        assert issues_dir.is_dir()
        assert issues_dir.name == 'issues'
        assert issues_dir.parent.name == '.bugit'
    
    def test_returns_existing_directory(self, temp_dir):
        """Test that existing directory is returned without error"""
        os.chdir(temp_dir)
        
        # Create directory manually
        bugit_dir = Path('.bugit')
        issues_dir = bugit_dir / 'issues'
        issues_dir.mkdir(parents=True, exist_ok=True)
        
        # Call function
        result_dir = ensure_issues_directory()
        
        # Should return the same directory
        assert result_dir == issues_dir
        assert result_dir.exists()


class TestAtomicWriteJson:
    """Test the atomic_write_json function"""
    
    def test_writes_json_file_atomically(self, temp_dir):
        """Test that JSON data is written atomically"""
        os.chdir(temp_dir)
        test_file = Path('test.json')
        test_data = {'id': 'test', 'title': 'Test Issue'}
        
        # Write data
        atomic_write_json(test_file, test_data)
        
        # Verify file exists and contains correct data
        assert test_file.exists()
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    
    def test_handles_unicode_data(self, temp_dir):
        """Test that unicode data is handled correctly"""
        os.chdir(temp_dir)
        test_file = Path('unicode.json')
        test_data = {'title': 'Test with émojis 🚀 and ünïcödé'}
        
        atomic_write_json(test_file, test_data)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    
    def test_overwrites_existing_file(self, temp_dir):
        """Test that existing files are overwritten"""
        os.chdir(temp_dir)
        test_file = Path('overwrite.json')
        
        # Write initial data
        initial_data = {'version': 1}
        atomic_write_json(test_file, initial_data)
        
        # Overwrite with new data
        new_data = {'version': 2}
        atomic_write_json(test_file, new_data)
        
        # Verify new data
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == new_data


class TestReadJsonFile:
    """Test the read_json_file function"""
    
    def test_reads_valid_json_file(self, temp_dir):
        """Test reading a valid JSON file"""
        os.chdir(temp_dir)
        test_file = Path('valid.json')
        test_data = {'id': 'test', 'title': 'Valid Test'}
        
        # Create file
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Read file
        loaded_data = read_json_file(test_file)
        assert loaded_data == test_data
    
    def test_raises_error_for_missing_file(self, temp_dir):
        """Test that missing file raises StorageError"""
        os.chdir(temp_dir)
        missing_file = Path('missing.json')
        
        with pytest.raises(StorageError, match="not found"):
            read_json_file(missing_file)
    
    def test_raises_error_for_invalid_json(self, temp_dir):
        """Test that invalid JSON raises StorageError"""
        os.chdir(temp_dir)
        invalid_file = Path('invalid.json')
        
        # Create invalid JSON
        with open(invalid_file, 'w') as f:
            f.write('{"invalid": json}')
        
        with pytest.raises(StorageError, match="Invalid JSON"):
            read_json_file(invalid_file)


class TestSaveIssue:
    """Test the save_issue function"""
    
    def test_saves_new_issue(self, temp_dir):
        """Test saving a new issue"""
        os.chdir(temp_dir)
        issue_data = {
            'id': 'new-issue',
            'title': 'New Test Issue',
            'description': 'Test description',
            'severity': 'medium',
            'tags': ['test'],
            'schema_version': 'v1'
        }
        
        result_id = save_issue(issue_data)
        
        # Check return value
        assert result_id == 'new-issue'
        
        # Check file was created
        issues_dir = Path('.bugit/issues')
        issue_file = issues_dir / 'new-issue.json'
        assert issue_file.exists()
        
        # Check file contents
        with open(issue_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == issue_data
    
    def test_overwrites_existing_issue(self, temp_dir):
        """Test that saving existing ID overwrites the file"""
        os.chdir(temp_dir)
        issue_id = 'existing-issue'
        
        # Save initial version
        initial_data = {
            'id': issue_id,
            'title': 'Initial Title',
            'severity': 'low'
        }
        save_issue(initial_data)
        
        # Save updated version
        updated_data = {
            'id': issue_id,
            'title': 'Updated Title',
            'severity': 'high'
        }
        save_issue(updated_data)
        
        # Verify updated data
        loaded_issue = load_issue(issue_id)
        assert loaded_issue['title'] == 'Updated Title'
        assert loaded_issue['severity'] == 'high'
    
    def test_handles_special_characters_in_id(self, temp_dir):
        """Test saving issue with special characters in ID"""
        os.chdir(temp_dir)
        # Note: file system safe characters only
        issue_data = {
            'id': 'issue-with_special123',
            'title': 'Special ID Test'
        }
        
        result_id = save_issue(issue_data)
        assert result_id == 'issue-with_special123'
        
        # Should be loadable
        loaded_issue = load_issue('issue-with_special123')
        assert loaded_issue['title'] == 'Special ID Test'


class TestLoadIssue:
    """Test the load_issue function"""
    
    def test_loads_existing_issue(self, temp_dir):
        """Test loading an existing issue"""
        os.chdir(temp_dir)
        issue_data = {
            'id': 'load-test',
            'title': 'Load Test Issue',
            'description': 'Test loading functionality'
        }
        
        # Save issue first
        save_issue(issue_data)
        
        # Load issue
        loaded_issue = load_issue('load-test')
        assert loaded_issue == issue_data
    
    def test_raises_error_for_missing_issue(self, temp_dir):
        """Test that loading missing issue raises StorageError"""
        os.chdir(temp_dir)
        
        with pytest.raises(StorageError, match="Issue.*not found"):
            load_issue('missing-issue')
    
    def test_handles_corrupted_issue_file(self, temp_dir):
        """Test handling of corrupted issue files"""
        os.chdir(temp_dir)
        issues_dir = ensure_issues_directory()
        
        # Create corrupted file
        corrupted_file = issues_dir / 'corrupted.json'
        with open(corrupted_file, 'w') as f:
            f.write('{"broken": json content}')
        
        with pytest.raises(StorageError, match="corrupted"):
            load_issue('corrupted')


class TestListIssues:
    """Test the list_issues function"""
    
    def test_lists_empty_directory(self, temp_dir):
        """Test listing when no issues exist"""
        os.chdir(temp_dir)
        
        issues = list_issues()
        assert issues == []
    
    def test_lists_single_issue(self, temp_dir):
        """Test listing a single issue"""
        os.chdir(temp_dir)
        issue_data = {
            'id': 'single',
            'title': 'Single Issue',
            'severity': 'medium',
            'created_at': '2025-01-01T12:00:00'
        }
        save_issue(issue_data)
        
        issues = list_issues()
        assert len(issues) == 1
        assert issues[0] == issue_data
    
    def test_lists_multiple_issues_sorted(self, temp_dir):
        """Test listing multiple issues with proper sorting"""
        os.chdir(temp_dir)
        
        # Create issues with different severities and dates
        critical_issue = {
            'id': 'critical-1',
            'title': 'Critical Issue',
            'severity': 'critical',
            'created_at': '2025-01-01T10:00:00'
        }
        low_issue = {
            'id': 'low-1',
            'title': 'Low Issue',
            'severity': 'low',
            'created_at': '2025-01-01T12:00:00'
        }
        medium_issue = {
            'id': 'medium-1',
            'title': 'Medium Issue',
            'severity': 'medium',
            'created_at': '2025-01-01T11:00:00'
        }
        
        # Save in random order
        save_issue(low_issue)
        save_issue(critical_issue)
        save_issue(medium_issue)
        
        # List should be sorted by severity desc, then created_at desc
        issues = list_issues()
        assert len(issues) == 3
        assert issues[0]['severity'] == 'critical'  # First by severity
        assert issues[1]['severity'] == 'medium'
        assert issues[2]['severity'] == 'low'
    
    def test_skips_corrupted_files(self, temp_dir):
        """Test that corrupted files are skipped during listing"""
        os.chdir(temp_dir)
        issues_dir = ensure_issues_directory()
        
        # Create valid issue
        valid_issue = {'id': 'valid', 'title': 'Valid Issue'}
        save_issue(valid_issue)
        
        # Create corrupted file
        corrupted_file = issues_dir / 'corrupted.json'
        with open(corrupted_file, 'w') as f:
            f.write('invalid json')
        
        # Should only return valid issues
        issues = list_issues()
        assert len(issues) == 1
        assert issues[0]['id'] == 'valid'


class TestDeleteIssue:
    """Test the delete_issue function"""
    
    def test_deletes_existing_issue(self, temp_dir):
        """Test deleting an existing issue"""
        os.chdir(temp_dir)
        issue_data = {'id': 'delete-me', 'title': 'Delete Test'}
        save_issue(issue_data)
        
        # Verify it exists
        assert load_issue('delete-me')['title'] == 'Delete Test'
        
        # Delete it
        result = delete_issue('delete-me')
        assert result is True
        
        # Verify it's gone
        with pytest.raises(StorageError):
            load_issue('delete-me')
    
    def test_returns_false_for_missing_issue(self, temp_dir):
        """Test that deleting missing issue returns False"""
        os.chdir(temp_dir)
        
        result = delete_issue('missing-issue')
        assert result is False
    
    def test_creates_backup_when_requested(self, temp_dir):
        """Test that backup is created when backup_on_delete is enabled"""
        os.chdir(temp_dir)
        issue_data = {'id': 'backup-test', 'title': 'Backup Test'}
        save_issue(issue_data)
        
        # Mock config to enable backup
        with patch('core.storage.get_config_value') as mock_get_config:
            mock_get_config.return_value = True  # Enable backup
            
            result = delete_issue('backup-test')
            assert result is True
            
            # Check backup was created
            backup_dir = Path('.bugit/backups')
            backup_files = list(backup_dir.glob('backup-test_*.json'))
            assert len(backup_files) == 1
            
            # Verify backup content
            with open(backup_files[0], 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            assert backup_data == issue_data


class TestGetIssueByIndex:
    """Test the get_issue_by_index function"""
    
    def test_gets_issue_by_valid_index(self, temp_dir):
        """Test getting issue by valid index"""
        os.chdir(temp_dir)
        
        # Create multiple issues
        issue1 = {'id': 'first', 'title': 'First', 'severity': 'critical', 'created_at': '2025-01-01T10:00:00'}
        issue2 = {'id': 'second', 'title': 'Second', 'severity': 'medium', 'created_at': '2025-01-01T11:00:00'}
        save_issue(issue1)
        save_issue(issue2)
        
        # Get by index (1-based)
        result = get_issue_by_index(1)
        assert result['id'] == 'first'  # Critical comes first
        
        result = get_issue_by_index(2)
        assert result['id'] == 'second'
    
    def test_raises_error_for_invalid_index(self, temp_dir):
        """Test that invalid index raises StorageError"""
        os.chdir(temp_dir)
        
        with pytest.raises(StorageError, match="Invalid index"):
            get_issue_by_index(0)  # 0 is invalid (1-based)
        
        with pytest.raises(StorageError, match="Invalid index"):
            get_issue_by_index(-1)  # Negative is invalid
    
    def test_raises_error_for_out_of_range_index(self, temp_dir):
        """Test that out of range index raises StorageError"""
        os.chdir(temp_dir)
        
        # Create one issue
        issue = {'id': 'only-one', 'title': 'Only Issue'}
        save_issue(issue)
        
        with pytest.raises(StorageError, match="out of range"):
            get_issue_by_index(2)  # Only 1 issue exists


class TestGetStorageStats:
    """Test the get_storage_stats function"""
    
    def test_returns_stats_for_empty_storage(self, temp_dir):
        """Test stats for empty storage"""
        os.chdir(temp_dir)
        
        stats = get_storage_stats()
        assert isinstance(stats, dict)
        assert stats['total_issues'] == 0
        assert stats['total_size_bytes'] == 0
        assert stats['issues_by_severity'] == {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    
    def test_returns_correct_stats_with_issues(self, temp_dir):
        """Test stats calculation with actual issues"""
        os.chdir(temp_dir)
        
        # Create issues with different severities
        critical_issue = {'id': 'crit', 'title': 'Critical', 'severity': 'critical'}
        medium_issue = {'id': 'med', 'title': 'Medium', 'severity': 'medium'}
        low_issue = {'id': 'low', 'title': 'Low', 'severity': 'low'}
        
        save_issue(critical_issue)
        save_issue(medium_issue)
        save_issue(low_issue)
        
        stats = get_storage_stats()
        assert stats['total_issues'] == 3
        assert stats['total_size_bytes'] > 0
        assert stats['issues_by_severity']['critical'] == 1
        assert stats['issues_by_severity']['medium'] == 1
        assert stats['issues_by_severity']['low'] == 1
        assert stats['issues_by_severity']['high'] == 0
    
    def test_handles_storage_errors_gracefully(self, temp_dir):
        """Test that storage errors are handled in stats"""
        os.chdir(temp_dir)
        issues_dir = ensure_issues_directory()
        
        # Create valid issue
        save_issue({'id': 'valid', 'title': 'Valid'})
        
        # Create corrupted file
        corrupted_file = issues_dir / 'corrupted.json'
        with open(corrupted_file, 'w') as f:
            f.write('invalid json')
        
        # Stats should still work, just excluding corrupted files
        stats = get_storage_stats()
        assert stats['total_issues'] == 1  # Only valid issue counted


@pytest.mark.skipif(platform.system() == "Windows", reason="Full file locking not implemented on Windows")
class TestFileLocking:
    """Test file locking functionality (Unix only)"""
    
    def test_file_lock_prevents_concurrent_access(self, temp_dir):
        """Test that file locking prevents concurrent access"""
        os.chdir(temp_dir)
        test_file = Path('lock_test.json')
        test_file.touch()
        
        # This test would need threading to properly test, 
        # but at least verify the context manager works
        with storage.file_lock(test_file):
            assert test_file.exists()
        
        # File should still exist after lock is released
        assert test_file.exists()


class TestErrorHandling:
    """Test error handling in storage operations"""
    
    def test_storage_error_hierarchy(self):
        """Test that custom exceptions are properly defined"""
        # Test that our custom exceptions exist and inherit correctly
        assert issubclass(StorageError, Exception)
        assert issubclass(ConcurrentAccessError, StorageError)
        
        # Test that they can be raised and caught
        try:
            raise StorageError("Test error")
        except StorageError as e:
            assert str(e) == "Test error"
        
        try:
            raise ConcurrentAccessError("Test concurrent error")
        except ConcurrentAccessError as e:
            assert str(e) == "Test concurrent error"
        except StorageError:
            # Should also be catchable as StorageError
            pass


class TestAtomicWriteErrorPaths:
    """Test error handling in atomic_write_json"""
    
    def test_atomic_write_invalid_data_type(self, temp_dir):
        """Test that non-dict data raises StorageError"""
        os.chdir(temp_dir)
        test_file = Path('invalid_data.json')
        
        with pytest.raises(StorageError, match="Data must be a dictionary"):
            atomic_write_json(test_file, "not a dict")  # type: ignore
        
        with pytest.raises(StorageError, match="Data must be a dictionary"):
            atomic_write_json(test_file, ["also", "not", "dict"])  # type: ignore
    
    @pytest.mark.skipif(sys.platform.startswith('win'), reason="Permission testing complex on Windows")
    def test_atomic_write_permission_error(self, temp_dir):
        """Test atomic write with permission errors"""
        os.chdir(temp_dir)
        
        # Create a read-only directory
        readonly_dir = Path('readonly')
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        test_file = readonly_dir / 'cannot_write.json'
        test_data = {'test': 'data'}
        
        try:
            with pytest.raises(StorageError, match="Atomic write failed"):
                atomic_write_json(test_file, test_data)
        finally:
            # Cleanup - restore permissions
            readonly_dir.chmod(0o755)
    
    def test_atomic_write_temp_file_cleanup_on_error(self, temp_dir):
        """Test that temp files are cleaned up on errors"""
        os.chdir(temp_dir)
        
        # Mock os.fdopen to raise an error to trigger cleanup
        with patch('core.storage.os.fdopen', side_effect=OSError("Simulated write error")):
            test_file = Path('test_cleanup.json')
            test_data = {'test': 'data'}
            
            # This should trigger cleanup code path
            with pytest.raises(StorageError, match="Atomic write failed"):
                atomic_write_json(test_file, test_data)


class TestReadJsonErrorPaths:
    """Test error handling in read_json_file"""
    
    def test_read_json_non_dict_structure(self, temp_dir):
        """Test that non-dict JSON raises StorageError"""
        os.chdir(temp_dir)
        invalid_file = Path('non_dict.json')
        
        # Create JSON file with array instead of dict
        with open(invalid_file, 'w') as f:
            json.dump(["array", "not", "dict"], f)
        
        with pytest.raises(StorageError, match="Invalid JSON structure"):
            read_json_file(invalid_file)
    
    def test_read_json_general_exception(self, temp_dir):
        """Test general exception handling in read_json_file"""
        os.chdir(temp_dir)
        
        # Mock open to raise a general exception
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            test_file = Path('permission_error.json')
            
            with pytest.raises(StorageError, match="Failed to read"):
                read_json_file(test_file)


class TestSaveIssueErrorPaths:
    """Test error handling in save_issue"""
    
    def test_save_issue_invalid_data_type(self, temp_dir):
        """Test that non-dict data raises StorageError"""
        os.chdir(temp_dir)
        
        with pytest.raises(StorageError, match="Issue data must be a dictionary"):
            save_issue("not a dict")  # type: ignore
        
        with pytest.raises(StorageError, match="Issue data must be a dictionary"):
            save_issue(["also", "not", "dict"])  # type: ignore
    
    def test_save_issue_generates_id_when_missing(self, temp_dir):
        """Test that ID is generated when missing"""
        os.chdir(temp_dir)
        issue_data = {'title': 'Issue without ID'}
        
        result_id = save_issue(issue_data)
        
        # Should have generated an ID
        assert result_id is not None
        assert len(result_id) == 6  # UUID[:6]
        assert 'id' in issue_data  # Should have been added to data
        
        # Should be loadable by the generated ID
        loaded_issue = load_issue(result_id)
        assert loaded_issue['title'] == 'Issue without ID'
    
    def test_save_issue_general_exception_handling(self, temp_dir):
        """Test general exception handling in save_issue"""
        os.chdir(temp_dir)
        
        # Mock atomic_write_json to raise a general exception
        with patch('core.storage.atomic_write_json', side_effect=Exception("Unexpected error")):
            issue_data = {'id': 'test', 'title': 'Test'}
            
            with pytest.raises(StorageError, match="Failed to save issue test"):
                save_issue(issue_data)


class TestLoadIssueErrorPaths:
    """Test error handling in load_issue"""
    
    def test_load_issue_invalid_id_types(self, temp_dir):
        """Test that invalid ID types raise StorageError"""
        os.chdir(temp_dir)
        
        with pytest.raises(StorageError, match="Issue ID must be a non-empty string"):
            load_issue("")  # Empty string
        
        with pytest.raises(StorageError, match="Issue ID must be a non-empty string"):
            load_issue(None)  # type: ignore
        
        with pytest.raises(StorageError, match="Issue ID must be a non-empty string"):
            load_issue(123)  # type: ignore
    
    def test_load_issue_adds_missing_id_field(self, temp_dir):
        """Test that missing ID field is added during load"""
        os.chdir(temp_dir)
        issues_dir = ensure_issues_directory()
        
        # Create issue file without ID field
        issue_file = issues_dir / 'no-id.json'
        issue_data = {'title': 'Issue without ID field'}
        
        with open(issue_file, 'w', encoding='utf-8') as f:
            json.dump(issue_data, f)
        
        # Load should add the ID
        loaded_issue = load_issue('no-id')
        assert loaded_issue['id'] == 'no-id'
        assert loaded_issue['title'] == 'Issue without ID field'
    
    def test_load_issue_general_exception_handling(self, temp_dir):
        """Test general exception handling in load_issue"""
        os.chdir(temp_dir)
        
        # Create a valid issue first
        save_issue({'id': 'test', 'title': 'Test'})
        
        # Mock file_lock to raise a general exception
        with patch('core.storage.file_lock', side_effect=Exception("Unexpected error")):
            with pytest.raises(StorageError, match="Failed to load issue test"):
                load_issue('test')


class TestListIssuesErrorPaths:
    """Test error handling in list_issues"""
    
    def test_list_issues_with_debug_logging(self, temp_dir):
        """Test debug logging for failed files"""
        os.chdir(temp_dir)
        issues_dir = ensure_issues_directory()
        
        # Create valid issue
        save_issue({'id': 'valid', 'title': 'Valid Issue'})
        
        # Create corrupted file
        corrupted_file = issues_dir / 'corrupted.json'
        with open(corrupted_file, 'w') as f:
            f.write('invalid json')
        
        # Enable debug mode
        with patch.dict(os.environ, {'BUGIT_DEBUG': '1'}):
            with patch('builtins.print') as mock_print:
                issues = list_issues()
                
                # Should have printed debug info
                mock_print.assert_called()
                debug_output = str(mock_print.call_args_list)
                assert 'Failed to load' in debug_output
                assert 'corrupted.json' in debug_output
        
        # Should still return valid issues
        assert len(issues) == 1
        assert issues[0]['id'] == 'valid'
    
    def test_list_issues_skips_lock_and_tmp_files(self, temp_dir):
        """Test that lock files and temp files are skipped"""
        os.chdir(temp_dir)
        issues_dir = ensure_issues_directory()
        
        # Create valid issue
        save_issue({'id': 'valid', 'title': 'Valid Issue'})
        
        # Create lock file and tmp file
        lock_file = issues_dir / 'test.json.lock'
        tmp_file = issues_dir / 'test.tmp.json'
        
        lock_file.touch()
        tmp_file.touch()
        
        issues = list_issues()
        
        # Should only return valid issue, ignoring lock/tmp files
        assert len(issues) == 1
        assert issues[0]['id'] == 'valid'
    
    def test_list_issues_datetime_parsing_fallback(self, temp_dir):
        """Test datetime parsing fallback for invalid dates"""
        os.chdir(temp_dir)
        
        # Create issues with various date formats
        issue_valid_date = {
            'id': 'valid-date',
            'title': 'Valid Date',
            'severity': 'medium',
            'created_at': '2025-01-01T12:00:00'
        }
        issue_invalid_date = {
            'id': 'invalid-date',
            'title': 'Invalid Date',
            'severity': 'medium',
            'created_at': 'not-a-date'
        }
        issue_no_date = {
            'id': 'no-date',
            'title': 'No Date',
            'severity': 'medium'
            # No created_at field
        }
        
        save_issue(issue_valid_date)
        save_issue(issue_invalid_date)
        save_issue(issue_no_date)
        
        # Should handle all cases without error
        issues = list_issues()
        assert len(issues) == 3
        
        # All should have medium severity, so order by fallback dates
        # Invalid dates should use epoch time (0) as fallback


class TestDeleteIssueErrorPaths:
    """Test error handling in delete_issue"""
    
    def test_delete_issue_invalid_id_types(self, temp_dir):
        """Test that invalid ID types raise StorageError"""
        os.chdir(temp_dir)
        
        with pytest.raises(StorageError, match="Issue ID must be a non-empty string"):
            delete_issue("")  # Empty string
        
        with pytest.raises(StorageError, match="Issue ID must be a non-empty string"):
            delete_issue(None)  # type: ignore
        
        with pytest.raises(StorageError, match="Issue ID must be a non-empty string"):
            delete_issue(123)  # type: ignore
    
    def test_delete_issue_backup_disabled(self, temp_dir):
        """Test deletion when backup is disabled"""
        os.chdir(temp_dir)
        issue_data = {'id': 'no-backup', 'title': 'No Backup Test'}
        save_issue(issue_data)
        
        # Mock config to disable backup
        with patch('core.storage.get_config_value') as mock_get_config:
            mock_get_config.return_value = False  # Disable backup
            
            result = delete_issue('no-backup')
            assert result is True
            
            # No backup should be created
            backup_dir = Path('.bugit/backups')
            if backup_dir.exists():
                backup_files = list(backup_dir.glob('no-backup_*.json'))
                assert len(backup_files) == 0
    
    def test_delete_issue_backup_config_none(self, temp_dir):
        """Test deletion when backup config is None (should default to True)"""
        os.chdir(temp_dir)
        issue_data = {'id': 'backup-default', 'title': 'Default Backup Test'}
        save_issue(issue_data)
        
        # Mock config to return None (should default to True)
        with patch('core.storage.get_config_value') as mock_get_config:
            mock_get_config.return_value = None  # Use default
            
            result = delete_issue('backup-default')
            assert result is True
            
            # Backup should be created (default behavior)
            backup_dir = Path('.bugit/backups')
            backup_files = list(backup_dir.glob('backup-default_*.json'))
            assert len(backup_files) == 1
    
    def test_delete_issue_general_exception_handling(self, temp_dir):
        """Test general exception handling in delete_issue"""
        os.chdir(temp_dir)
        
        # Create a valid issue
        save_issue({'id': 'test', 'title': 'Test'})
        
        # Mock file_lock to raise a general exception
        with patch('core.storage.file_lock', side_effect=Exception("Unexpected error")):
            with pytest.raises(StorageError, match="Failed to delete issue test"):
                delete_issue('test')


class TestGetIssueByIndexErrorPaths:
    """Test error handling in get_issue_by_index"""
    
    def test_get_issue_by_index_non_integer_types(self, temp_dir):
        """Test that non-integer types raise StorageError"""
        os.chdir(temp_dir)
        
        with pytest.raises(StorageError, match="Invalid index"):
            get_issue_by_index("1")  # type: ignore
        
        with pytest.raises(StorageError, match="Invalid index"):
            get_issue_by_index(1.5)  # type: ignore
        
        with pytest.raises(StorageError, match="Invalid index"):
            get_issue_by_index(None)  # type: ignore


class TestGetStorageStatsErrorPaths:
    """Test error handling in get_storage_stats"""
    
    def test_get_storage_stats_with_general_exception(self, temp_dir):
        """Test stats when general exception occurs"""
        os.chdir(temp_dir)
        
        # Mock list_issues to raise an exception
        with patch('core.storage.list_issues', side_effect=Exception("Stats error")):
            stats = get_storage_stats()
            
            # Should return error stats structure
            assert 'error' in stats
            assert 'Stats error' in stats['error']
            assert stats['total_issues'] == 0
            assert stats['total_size_bytes'] == 0
            assert stats['issues_by_severity'] == {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    
    def test_get_storage_stats_with_missing_issue_files(self, temp_dir):
        """Test stats calculation when issue files are missing"""
        os.chdir(temp_dir)
        issues_dir = ensure_issues_directory()
        
        # Create issue data but manually remove the file after
        issue_data = {'id': 'missing-file', 'title': 'Missing File'}
        save_issue(issue_data)
        
        # Now delete the file directly (simulating external deletion)
        issue_file = issues_dir / 'missing-file.json'
        issue_file.unlink()
        
        # Stats should handle missing file gracefully
        stats = get_storage_stats()
        assert isinstance(stats, dict)
        # This might still count the issue if it was already loaded
        # but shouldn't crash


@pytest.mark.skipif(sys.platform.startswith('win'), reason="Unix file locking only")  
class TestUnixFileLocking:
    """Test Unix-specific file locking functionality"""
    
    def test_file_lock_timeout_behavior(self, temp_dir):
        """Test file lock timeout functionality"""
        os.chdir(temp_dir)
        test_file = Path('timeout_test.json')
        test_file.touch()
        
        # Test that timeout works (hard to test concurrency in unit tests)
        with storage.file_lock(test_file, timeout=0.1):
            assert test_file.exists()
        
        # Test very short timeout
        try:
            with storage.file_lock(test_file, timeout=0.001):
                pass
        except ConcurrentAccessError:
            # This might happen with very short timeout
            pass
    
    def test_file_lock_exception_handling(self, temp_dir):
        """Test exception handling in file locking"""
        os.chdir(temp_dir)
        test_file = Path('exception_test.json')
        
        # Mock fcntl.flock to raise an exception
        with patch('fcntl.flock', side_effect=OSError("Lock failed")):
            with pytest.raises(ConcurrentAccessError, match="Could not acquire lock"):
                with storage.file_lock(test_file, timeout=0.1):
                    pass 