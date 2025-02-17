import unittest
import json
import os
import logging
import time
import re
from backend_python import (
    convert_mp3_to_wav,
    load_vosk_model,
    transcribe_audio,
    format_transcriptions
)

from tcb2 import process_video_transcript, extract_video_id



# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def save_results(results, filename="test_results.json"):
    """ Saves the test results in a structured JSON file. """
    with open(filename, "w") as file:
        json.dump(results, file, indent=4)
    logging.info(f"Test results saved to {filename}")

class TestVideoTranscription(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        logging.info("Starting Test Suite for Video Transcription")
        cls.test_results = []  # Store all test results

    def test_extract_video_id(self):
        """Test if video ID is correctly extracted from different YouTube URL formats."""
        test_cases = {
            "https://www.youtube.com/watch?v=abc123": "abc123",
            "https://youtu.be/xyz789": "xyz789",
            "https://www.youtube.com/embed/lmn456": "lmn456",
            "https://invalid.com/video": None,
        }
        for url, expected in test_cases.items():
            with self.subTest(url=url):
                result = extract_video_id(url)
                self.assertEqual(result, expected)
                self.test_results.append({
                    "test": "extract_video_id",
                    "input": url,
                    "expected": expected,
                    "actual": result,
                    "status": "pass" if result == expected else "fail"
                })

    def test_process_video_transcript(self):
        """ Test end-to-end video transcription flow, including download, conversion, and transcription. """
        video_url = "https://youtu.be/jmmW0F0biz0"
        try:
            start_time = time.time()
            result = process_video_transcript(video_url)
            end_time = time.time()
            
            # Basic validity check
            self.assertTrue(isinstance(result, str) and len(result) > 10)
            
            self.test_results.append({
                "test": "process_video_transcript",
                "input": video_url,
                "expected": "Valid transcript string",
                "actual": result[:100] + "...",  # Store only the first 100 chars
                "execution_time": round(end_time - start_time, 2),
                "status": "pass"
            })
        except Exception as e:
            self.test_results.append({
                "test": "process_video_transcript",
                "input": video_url,
                "expected": "Valid transcript string",
                "actual": str(e),
                "status": "fail"
            })
            raise e  # Re-raise for debugging

    def test_invalid_url(self):
        """ Test handling of an invalid YouTube URL. """
        with self.assertRaises(ValueError):
            process_video_transcript("invalid_url")
        self.test_results.append({
            "test": "test_invalid_url",
            "input": "invalid_url",
            "expected": "ValueError",
            "actual": "ValueError raised",
            "status": "pass"
        })

    @classmethod
    def tearDownClass(cls):
        save_results(cls.test_results)
        logging.info("All tests completed.")

if __name__ == "__main__":
    unittest.main()
