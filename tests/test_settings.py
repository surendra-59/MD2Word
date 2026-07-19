import unittest
import os
import json
import tempfile
from converter.config.settings import AppSettings

class TestSettings(unittest.TestCase):
    def test_load_corrupt_json(self):
        # Create a corrupt JSON file
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, 'w') as f:
            f.write("{ invalid json structure")
        
        try:
            # Should not crash, should return default settings
            settings = AppSettings.load(path)
            self.assertIsInstance(settings, AppSettings)
            
            # Check a default value is present
            default_settings = AppSettings()
            self.assertEqual(settings.output_prefix, default_settings.output_prefix)
            self.assertEqual(settings.code_font_size, default_settings.code_font_size)
        finally:
            os.remove(path)

if __name__ == '__main__':
    unittest.main()
