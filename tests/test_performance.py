"""
Performance tests for BugIt CLI.
Tests system behavior under load and measures performance characteristics.
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock
from core import storage, model, schema


@pytest.mark.performance
class TestStoragePerformance:
    """Performance tests for storage operations"""
    
    def test_large_issue_list_performance(self, temp_dir, issue_factory, performance_monitor):
        """Test performance with large number of issues"""
        # Create a large number of issues
        num_issues = 100
        
        start_time = time.time()
        
        # Create issues
        for i in range(num_issues):
            issue = issue_factory.create_issue(
                title=f"Performance Test Issue {i+1}",
                issue_id=f"perf-test-{i+1}",
                severity=["low", "medium", "high", "critical"][i % 4]
            )
            storage.save_issue(issue)
        
        creation_time = time.time() - start_time
        
        # Test listing performance
        start_time = time.time()
        all_issues = storage.list_issues()
        list_time = time.time() - start_time
        
        # Verify results
        assert len(all_issues) == num_issues
        
        # Performance assertions
        assert creation_time < 10.0, f"Creation took too long: {creation_time:.2f}s"
        assert list_time < 2.0, f"Listing took too long: {list_time:.2f}s"
        
        print(f"Created {num_issues} issues in {creation_time:.3f}s")
        print(f"Listed {num_issues} issues in {list_time:.3f}s")
    
    def test_concurrent_storage_access(self, temp_dir, issue_factory):
        """Test concurrent access to storage operations"""
        num_threads = 10
        issues_per_thread = 5
        
        def create_issues(thread_id):
            """Create issues in a thread"""
            created_ids = []
            for i in range(issues_per_thread):
                issue = issue_factory.create_issue(
                    title=f"Concurrent Test {thread_id}-{i+1}",
                    issue_id=f"concurrent-{thread_id}-{i+1}"
                )
                issue_id = storage.save_issue(issue)
                created_ids.append(issue_id)
            return created_ids
        
        start_time = time.time()
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_issues, i) for i in range(num_threads)]
            
            all_created_ids = []
            for future in as_completed(futures):
                created_ids = future.result()
                all_created_ids.extend(created_ids)
        
        concurrent_time = time.time() - start_time
        
        # Verify all issues were created
        all_issues = storage.list_issues()
        expected_total = num_threads * issues_per_thread
        
        assert len(all_issues) == expected_total
        assert len(all_created_ids) == expected_total
        
        # Performance assertion
        assert concurrent_time < 5.0, f"Concurrent operations took too long: {concurrent_time:.2f}s"
        
        print(f"Created {expected_total} issues concurrently in {concurrent_time:.3f}s")
    
    def test_memory_usage_with_large_dataset(self, temp_dir, issue_factory):
        """Test memory usage doesn't grow excessively with large datasets"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create a large dataset
        num_issues = 500
        
        for i in range(num_issues):
            issue = issue_factory.create_issue(
                title=f"Memory Test Issue {i+1}",
                description=f"This is a longer description for memory test issue {i+1}. " * 10,
                issue_id=f"memory-test-{i+1}",
                tags=[f"tag{j}" for j in range(i % 10)]  # Variable number of tags
            )
            storage.save_issue(issue)
            
            # Check memory every 100 issues
            if (i + 1) % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_growth = current_memory - initial_memory
                
                # Memory shouldn't grow excessively (arbitrary limit for test)
                assert memory_growth < 100, f"Memory growth too large: {memory_growth:.2f}MB after {i+1} issues"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - initial_memory
        
        print(f"Memory growth for {num_issues} issues: {total_growth:.2f}MB")
        assert total_growth < 200, f"Total memory growth too large: {total_growth:.2f}MB"


@pytest.mark.performance 
@pytest.mark.slow
class TestModelPerformance:
    """Performance tests for model processing (with mocks to avoid API costs)"""
    
    def test_model_processing_batch_performance(self, mock_openai_client, mock_config_operations):
        """Test performance of processing multiple descriptions"""
        descriptions = [
            "System crash on startup",
            "Login button not working", 
            "Database connection timeout",
            "UI button misaligned",
            "Camera crash when recording",
            "Network request fails",
            "File upload broken",
            "Search feature slow",
            "Memory leak in application",
            "Performance degradation"
        ]
        
        # Configure mock response
        mock_response = {
            'title': 'Test Issue',
            'description': 'Test description',
            'severity': 'medium',
            'type': 'bug',
            'tags': ['test']
        }
        mock_openai_client.invoke.return_value.content = str(mock_response).replace("'", '"')
        
        start_time = time.time()
        
        results = []
        for description in descriptions:
            result = model.process_description(description)
            results.append(result)
        
        processing_time = time.time() - start_time
        
        # Verify all processed successfully
        assert len(results) == len(descriptions)
        for result in results:
            assert 'title' in result
            assert 'severity' in result
        
        # Performance assertion
        avg_time_per_request = processing_time / len(descriptions)
        assert avg_time_per_request < 0.1, f"Average processing time too slow: {avg_time_per_request:.3f}s"
        
        print(f"Processed {len(descriptions)} descriptions in {processing_time:.3f}s")
        print(f"Average time per request: {avg_time_per_request:.3f}s")
    
    def test_model_processing_retry_performance(self, mock_config_operations):
        """Test performance impact of retry logic"""
        retry_counts = [1, 2, 3]  # Test different retry scenarios
        
        for max_retries in retry_counts:
            with patch('core.model.ChatOpenAI') as mock_openai:
                # Configure mock to fail then succeed
                mock_client = MagicMock()
                
                # Fail for max_retries times, then succeed
                call_count = 0
                def side_effect(*args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    if call_count <= max_retries:
                        raise Exception("Simulated failure")
                    else:
                        mock_response = MagicMock()
                        mock_response.content = '{"title": "Test", "description": "Test", "severity": "medium", "type": "bug", "tags": ["test"]}'
                        return mock_response
                
                mock_client.invoke.side_effect = side_effect
                mock_openai.return_value = mock_client
                
                start_time = time.time()
                
                # Patch the config to return our test retry limit
                test_config = {'openai_api_key': 'test-key', 'retry_limit': max_retries + 1}
                with patch('core.model.load_config', return_value=test_config):
                    result = model.process_description("Test description")
                
                retry_time = time.time() - start_time
                
                # Should eventually succeed
                assert 'title' in result
                
                # Time should increase with more retries, but not excessively
                assert retry_time < 1.0, f"Retry scenario took too long: {retry_time:.3f}s for {max_retries} retries"
                
                print(f"Retry scenario ({max_retries} retries) took {retry_time:.3f}s")


@pytest.mark.performance
class TestSchemaValidationPerformance:
    """Performance tests for schema validation"""
    
    def test_bulk_validation_performance(self, performance_monitor):
        """Test validation performance with large datasets"""
        # Create test data
        test_data = []
        for i in range(1000):
            data = {
                'title': f'Test Issue {i+1}',
                'description': f'This is test issue number {i+1} with some description content.',
                'severity': ['low', 'medium', 'high', 'critical'][i % 4],
                'type': ['bug', 'feature', 'chore'][i % 3],
                'tags': [f'tag{j}' for j in range(i % 5)]
            }
            test_data.append(data)
        
        start_time = time.time()
        
        # Validate all data
        validated_data = []
        for data in test_data:
            validated = schema.validate_or_default(data)
            validated_data.append(validated)
        
        validation_time = time.time() - start_time
        
        # Verify results
        assert len(validated_data) == len(test_data)
        for validated in validated_data:
            assert 'id' in validated
            assert 'created_at' in validated
            assert validated['schema_version'] == 'v1'
        
        # Performance assertion
        avg_time_per_validation = validation_time / len(test_data)
        assert avg_time_per_validation < 0.001, f"Validation too slow: {avg_time_per_validation:.4f}s per item"
        
        print(f"Validated {len(test_data)} items in {validation_time:.3f}s")
        print(f"Average time per validation: {avg_time_per_validation:.4f}s")
    
    def test_validation_edge_cases_performance(self):
        """Test performance with validation edge cases"""
        edge_cases = [
            {'title': 'A' * 200, 'description': 'Long title test'},  # Long title
            {'title': 'Test', 'description': 'A' * 10000},  # Long description  
            {'title': 'Test', 'tags': ['tag'] * 50},  # Many tags
            {'title': 'Test', 'severity': 'invalid'},  # Invalid severity
            {'title': 'Test', 'type': 'invalid'},  # Invalid type
        ]
        
        start_time = time.time()
        
        for case in edge_cases:
            result = schema.validate_or_default(case)
            # Basic validation that it succeeds
            assert 'title' in result
            assert 'severity' in result
        
        edge_case_time = time.time() - start_time
        
        # Should handle edge cases quickly
        assert edge_case_time < 0.1, f"Edge case validation too slow: {edge_case_time:.3f}s"
        
        print(f"Edge case validation completed in {edge_case_time:.3f}s")


@pytest.mark.performance
@pytest.mark.slow
class TestIntegrationPerformance:
    """End-to-end performance tests"""
    
    def test_full_workflow_performance(self, temp_dir, mock_openai_client, mock_config_operations):
        """Test performance of complete workflow: create -> list -> show -> edit -> delete"""
        # Configure mock
        mock_response = {
            'title': 'Performance Test Issue',
            'description': 'Test description', 
            'severity': 'medium',
            'type': 'bug',
            'tags': ['performance', 'test']
        }
        mock_openai_client.invoke.return_value.content = str(mock_response).replace("'", '"')
        
        num_iterations = 50
        
        start_time = time.time()
        
        issue_ids = []
        
        for i in range(num_iterations):
            # Create
            result = model.process_description(f"Performance test issue {i+1}")
            validated = schema.validate_or_default(result)
            issue_id = storage.save_issue(validated)
            issue_ids.append(issue_id)
            
            # Show (every 10th issue)
            if i % 10 == 0:
                loaded = storage.load_issue(issue_id)
                assert loaded['id'] == issue_id
            
            # List (every 20th iteration)
            if i % 20 == 0:
                all_issues = storage.list_issues()
                assert len(all_issues) == i + 1
        
        # Bulk delete
        for issue_id in issue_ids:
            storage.delete_issue(issue_id)
        
        total_time = time.time() - start_time
        
        # Performance assertions
        avg_time_per_workflow = total_time / num_iterations
        assert avg_time_per_workflow < 0.1, f"Workflow too slow: {avg_time_per_workflow:.3f}s per iteration"
        
        print(f"Completed {num_iterations} full workflows in {total_time:.3f}s")
        print(f"Average time per workflow: {avg_time_per_workflow:.3f}s")


# Benchmark fixtures and utilities
@pytest.fixture
def benchmark_runner():
    """Utility for running performance benchmarks"""
    class BenchmarkRunner:
        def __init__(self):
            self.results = {}
        
        def run_benchmark(self, name, func, iterations=10):
            """Run a function multiple times and record performance"""
            times = []
            
            for _ in range(iterations):
                start = time.time()
                result = func()
                end = time.time()
                times.append(end - start)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            self.results[name] = {
                'avg': avg_time,
                'min': min_time,
                'max': max_time,
                'iterations': iterations
            }
            
            return result, avg_time
        
        def print_results(self):
            """Print benchmark results"""
            print("\n=== Performance Benchmark Results ===")
            for name, stats in self.results.items():
                print(f"{name}:")
                print(f"  Average: {stats['avg']:.4f}s")
                print(f"  Min: {stats['min']:.4f}s")  
                print(f"  Max: {stats['max']:.4f}s")
                print(f"  Iterations: {stats['iterations']}") 