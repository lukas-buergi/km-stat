import unittest
import structureLists2

class TestEnumerationBasicIdentity(unittest.TestCase):
  def testSingleLineChar(self):
    testIn = ['a.: Lalala\n',
              '  a. : Lalala\r\n'
              ]
    for line in testIn:
      with self.subTest(line=line):
        sl = structureLists2.structuredList([line], structureLists2.enumerationChar)
        sl.parse()
        self.assertEqual(sl.get(), testIn[0])

  def testSingleLineArabic(self):
    testIn = ['1.: Lalala\n',
              '  1. : Lalala\r\n'
              ]
    for line in testIn:
      with self.subTest(line=line):
        sl = structureLists2.structuredList([line], structureLists2.enumerationArabic)
        sl.parse()
        self.assertEqual(sl.get(), testIn[0])

  def testMultiLineChar(self):
    testIn = ['a.: Lalala\n',
              'b.: Blabla\n',
              'c.: Tralala\n',
              ]
    sl = structureLists2.structuredList(testIn, structureLists2.enumerationChar)
    sl.parse()
    self.assertEqual(sl.get().splitlines(), testIn)

  def testMultiLineArabic(self):
    testIn = ['1.: Lalala\n',
              '2.: Blabla\n',
              '3.: Tralala\n',
              ]
    sl = structureLists2.structuredList(testIn, structureLists2.enumerationArabic)
    sl.parse()
    self.assertEqual(sl.get().splitlines(), testIn)
    
class TestEnumerationBasic(unittest.TestCase):
  def testSingleLineChar(self):
    testIn = ['a. Lalala\n']
    sl = structureLists2.structuredList(testIn, structureLists2.enumerationChar)
    sl.parse()
    self.assertEqual(sl.get(), 'a.: Lalala\n')

  def testSingleLineArabic(self):
    testIn = ['1. Lalala\n']
    sl = structureLists2.structuredList(testIn, structureLists2.enumerationArabic)
    sl.parse()
    self.assertEqual(sl.get(), '1.: Lalala\n')
    
  def testMultiLineChar(self):
    testIn = ['	a. Lalala\n',
              'b. Blabla\r\n',
              ' c. Tralala \n	',
              ]
    testOut = ['a.: Lalala',
              'b.: Blabla',
              'c.: Tralala',
              ]
    sl = structureLists2.structuredList(testIn, structureLists2.enumerationChar)
    sl.parse()
    self.assertEqual(sl.get().splitlines(), testOut)

  def testMultiLineArabic(self):
    testIn = ['1.		Lalala\r\n',
              ' 2.: Blabla\n  ',
              '	3. Tralala	 ',
              ]
    testOut = ['1.: Lalala',
              '2.: Blabla',
              '3.: Tralala',
              ]
    sl = structureLists2.structuredList(testIn, structureLists2.enumerationArabic)
    sl.parse()
    self.assertEqual(sl.get().splitlines(), testOut)

class TestEnumerationCatchAll(unittest.TestCase):
  def testArabicNested(self):
    testIn = ['1.		Lalala\r\n',
              ' 2. Blabla\n  ',
              '	1. Tralala	 ',
              '2. Lolo',
              '3. Lala',
              '3. Li',
              ]
    testOut = [ '1.: Lalala',
                '2.: Blabla',
                '2.1.: Tralala',
                '2.2.: Lolo',
                '2.3.: Lala',
                '3.: Li',
              ]
    sl = structureLists2.structuredList(testIn, structureLists2.enumerationCatchAll)
    sl.parse()
    self.assertEqual(sl.get().splitlines(), testOut)

if __name__ == '__main__':
  unittest.main()
