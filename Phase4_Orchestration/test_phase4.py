"""
test_phase4.py
Unit tests for the Phase 4 Orchestrator
Uses mocking to test logic flow without actually triggering scraping/LLM API calls.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from main_orchestrator import run_pipeline
except ImportError:
    run_pipeline = None

class TestPhase4Orchestrator(unittest.TestCase):

    def setUp(self):
        # We only run these tests if the orchestrator was successfully imported
        if run_pipeline is None:
            self.skipTest("main_orchestrator could not be imported")

    @patch('main_orchestrator.run_phase1')
    @patch('main_orchestrator.run_phase2')
    @patch('main_orchestrator.run_phase3')
    @patch('main_orchestrator.os.path.exists')
    @patch('main_orchestrator.os.chdir')
    def test_pipeline_runs_all_phases_default(self, mock_chdir, mock_exists, mock_p3, mock_p2, mock_p1):
        # Default behavior: run everything, files don't exist
        mock_exists.return_value = False
        
        result = run_pipeline(skip_ingestion=False, skip_llm=False)
        
        self.assertTrue(result)
        mock_p1.assert_called_once()
        mock_p2.assert_called_once()
        mock_p3.assert_called_once()
        
        # Verify it changes directories to execute phases locally
        self.assertGreaterEqual(mock_chdir.call_count, 6)

    @patch('main_orchestrator.run_phase1')
    @patch('main_orchestrator.run_phase2')
    @patch('main_orchestrator.run_phase3')
    @patch('main_orchestrator.os.path.exists')
    @patch('main_orchestrator.os.chdir')
    def test_pipeline_skip_ingestion_when_file_exists(self, mock_chdir, mock_exists, mock_p3, mock_p2, mock_p1):
        # Force the CSV file check to return True so it skips
        mock_exists.side_effect = lambda x: str(x).endswith('.csv')
        
        result = run_pipeline(skip_ingestion=True, skip_llm=False)
        
        self.assertTrue(result)
        mock_p1.assert_not_called()  # Ingestion skipped
        mock_p2.assert_called_once() # LLM runs
        mock_p3.assert_called_once() # MCP runs

    @patch('main_orchestrator.run_phase1')
    @patch('main_orchestrator.run_phase2')
    @patch('main_orchestrator.run_phase3')
    @patch('main_orchestrator.os.path.exists')
    @patch('main_orchestrator.os.chdir')
    def test_pipeline_skip_llm_when_file_exists(self, mock_chdir, mock_exists, mock_p3, mock_p2, mock_p1):
        # Force the JSON file check to return True so it skips LLM
        mock_exists.side_effect = lambda x: str(x).endswith('.json')
        
        result = run_pipeline(skip_ingestion=True, skip_llm=True)
        
        self.assertTrue(result)
        mock_p1.assert_not_called()  # Ingestion skipped via override
        mock_p2.assert_not_called()  # LLM skipped
        mock_p3.assert_called_once() # MCP runs only

    @patch('main_orchestrator.run_phase1')
    @patch('main_orchestrator.run_phase2')
    @patch('main_orchestrator.run_phase3')
    @patch('main_orchestrator.os.path.exists')
    @patch('main_orchestrator.os.chdir')
    def test_pipeline_fails_on_phase1_error(self, mock_chdir, mock_exists, mock_p3, mock_p2, mock_p1):
        mock_exists.return_value = False
        mock_p1.side_effect = Exception("Phase 1 API Error")
        
        result = run_pipeline()
        
        self.assertFalse(result)
        mock_p1.assert_called_once()
        mock_p2.assert_not_called() # Does not proceed
        mock_p3.assert_not_called() # Does not proceed

if __name__ == '__main__':
    unittest.main()
