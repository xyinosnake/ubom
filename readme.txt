ubom - [U]nicode [BOM]
Made by Xyino Snake

    A trancoding tool for text files(like *.txt, *.c, *.h, *.cpp, *.hpp, *.nim, d etc).
    All written in a single python file.

    Lots of C/C++ code files written in utf-8 without BOM. Although the bom of the Utf-8 
was invented by Microsoft, now almost all platforms support the utf-8 BOM. It allows text 
files to avoid cluttering in almost all mainstream text file viewers, editors, and compilers. 
So utf-8 with BOM is good! To add BOM to utf-8 file, use ubom!
    In fact, ubom is a trancoding tool for text files. You can use it to transcode all the 
formats supported by the Python standard library. About the format string of Python standard
library, see https://docs.python.org/3/library/codecs.html for more details.

eg.
    ubom -f "C:/Code/" -s "gb2312"
    ubom -f "C:/Code/" -s "utf_8"
    ubom -f "C:/Code/" -s "gb2312" -d "utf_8_sig" -e ".txt, .c, .h, .cpp, .hpp, .py, .pyw, .d, .nim"
