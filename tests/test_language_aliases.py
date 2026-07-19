import unittest
from converter.core.language_aliases import normalize_code_fences

class TestLanguageAliases(unittest.TestCase):
    def test_language_aliases(self):
        markdown = "```py\ndef hello(): pass\n```\n\n```madeuplang\nsome code\n```"
        supported = {"python", "bash"} # dummy supported set
        
        normalized, unknown = normalize_code_fences(markdown, supported)
        
        # 'py' should be normalized to 'python'
        self.assertIn("```python", normalized)
        
        # 'madeuplang' is not supported
        self.assertIn("madeuplang", unknown)
        self.assertNotIn("python", unknown)

if __name__ == '__main__':
    unittest.main()
