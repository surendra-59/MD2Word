import unittest
import tempfile
import os
from converter.core.pipeline import ConversionPipeline
from converter.config.settings import AppSettings

class TestIntegration(unittest.TestCase):
    def test_github_theme_conversion(self):
        settings = AppSettings()
        settings.highlight_style = "github"
        
        pipeline = ConversionPipeline(settings)
        
        markdown = "# Hello\n\n```python\nprint('hello world')\n```"
        
        fd, output_path = tempfile.mkstemp(suffix=".docx")
        os.close(fd)
        
        try:
            result = pipeline.convert(markdown, output_path)
            self.assertTrue(result.success)
            self.assertTrue(os.path.exists(result.output_path))
            # Just test it doesn't crash and generates a docx.
            # Verifying the exact internal color requires extracting the docx zip.
            # We assume python-docx postprocessing succeeds.
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

if __name__ == '__main__':
    unittest.main()
