import unittest
from app.pipeline.stage02_chunker import SmartChunker

class TestChunker(unittest.TestCase):
    def setUp(self):
        # Standard production configuration
        self.chunker = SmartChunker(target_words=7000, max_words=10000)
        
    def test_chapter_boundaries(self):
        # Chapter 1 is exactly 6000 words
        p1 = "word " * 3000
        p2 = "word " * 3000
        ch1 = "Chapter 1\n\n" + p1 + "\n\n" + p2
        
        # Chapter 2 is 3000 words
        ch2 = "Chapter 2\n\n" + p1
        
        text = ch1 + "\n\n" + ch2
        
        chunks = self.chunker.chunk_text(text)
        
        # Because Chapter 1 is 6004 words (which is > 75% of 7000), 
        # hitting "Chapter 2" should cleanly force a split.
        self.assertEqual(len(chunks), 2)
        self.assertTrue(chunks[0].startswith("Chapter 1"))
        self.assertTrue(chunks[1].startswith("Chapter 2"))
        
        # Mathematically verify no data loss occurred
        self.assertTrue(self.chunker.validate_chunks(text, chunks))
        
    def test_hard_limit_split(self):
        # A single massive chapter with 12,000 words total, split into 3,000 word paragraphs.
        # It must force split before hitting 10,000 words.
        p1 = "word " * 3000
        text = "Chapter 1\n\n" + p1 + "\n\n" + p1 + "\n\n" + p1 + "\n\n" + p1
        
        chunks = self.chunker.chunk_text(text)
        
        # 3000 + 3000 + 3000 = 9000 (fits). 
        # Adding the 4th paragraph makes it 12000 (exceeds max_words 10000), so it splits.
        self.assertEqual(len(chunks), 2)
        self.assertEqual(self.chunker.get_word_count(chunks[0]), 9002)
        self.assertEqual(self.chunker.get_word_count(chunks[1]), 3000)
        
        self.assertTrue(self.chunker.validate_chunks(text, chunks))
        
    def test_validation_failure_on_data_loss(self):
        # Simulate a bug where the chunker lost text
        text = "word " * 5000
        chunks = ["word " * 4500] # 10% data loss
        
        self.assertFalse(self.chunker.validate_chunks(text, chunks))
        
if __name__ == '__main__':
    unittest.main()
