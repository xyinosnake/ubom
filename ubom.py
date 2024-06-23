
'''
ubom
    Made by Xyino Snake.
'''

import sys
import os
import platform
import codecs

from collections import namedtuple

#---declarations---
#enums
eBomCase = None
eBomBin  = None

eArgSingle = 0
eArgDouble = 1

#structs
dFileContent = None

#globals
gArgs:               map = None
gVersion:            str = "0.02"
gExtStr:             str = ".txt, .c, .h, .cpp, .hpp, .py, .pyw, .d, .di, .nim"
gUniqueArgMap:       map = None #转换参数为唯一参数
gArgMap:             map = None #映射参数类型
gBomBinToBomCase:    map = None
gBomCaseToFormatStr: map = None

#functions
ExtStrToExtList    = None
GetUniqueStr       = None
GetFileExt         = None
WalkFiles          = None
BomBinToBomCase    = None
BomCaseToFormatStr = None
ResolveFileBin     = None
GetFileContent     = None
GetFiles           = None
InitArgs           = None
GetVersion         = None
GetHelp            = None

#---definitions---

#enums
class eBomCase:
    NO_BOM   = 0
    UTF8     = 1
    UTF16_LE = 2
    UTF32_LE = 3
    UTF16_BE = 4
    UTF32_BE = 5

    def enums():
        return (
            eBomCase.NO_BOM,
            eBomCase.UTF8,
            eBomCase.UTF16_LE,
            eBomCase.UTF32_LE,
            eBomCase.UTF16_BE,
            eBomCase.UTF32_BE
        )

    def names(eCase):
        return (
            "NO_BOM",
            "UTF8",
            "UTF16_LE",
            "UTF32_LE",
            "UTF16_BE",
            "UTF32_BE"
        )[eCase]

class eBomBin:
    NO_BOM   = b""
    UTF8     = codecs.BOM_UTF8      # b'\xEF\xBB\xBF'
    UTF16_LE = codecs.BOM_UTF16_LE  # b'\xFF\xFE'
    UTF16_BE = codecs.BOM_UTF16_BE  # b'\xFE\xFF'
    UTF32_LE = codecs.BOM_UTF32_LE  # b'\xFF\xFE\x00\x00'
    UTF32_BE = codecs.BOM_UTF32_BE  # b'\x00\x00\xFE\xFF'

    def enums():
        return (
            eBomBin.UTF8,     # utf8的BOM很特别，不会有歧义，且最常见，应最先判断。
            eBomBin.UTF32_LE, # 先判断长的，再判断短的。
            eBomBin.UTF32_BE,
            eBomBin.UTF16_LE,
            eBomBin.UTF16_BE,
            eBomBin.NO_BOM
        )

#structs
dFileContent = namedtuple(
    "dFileFormat",
    "bomCase bomBin formatStr memBin")

#globals

gArgs = {
    "-h": False,
    "-v": False,
    "-f": "./", #current dir
    "-s": None, #Windows Default: "gb2312" Others(maybe): "utf_8"
    "-d": "utf_8_sig",
    "-e": gExtStr
}

gUniqueArgMap = {
    "/?":              "-h",
    "--help":          "-h",
    "--version":       "-v",
    "--file":          "-f",
    "--source_format": "-s",
    "--dest_format":   "-d",
    "--extentions":    "-e"
}

gArgMap = {
    "-h": eArgSingle,
    "-v": eArgSingle,
    "-f": eArgDouble,
    "-s": eArgDouble,
    "-d": eArgDouble,
    "-e": eArgDouble
}

gBomBinToBomCase = {
    eBomBin.NO_BOM:   eBomCase.NO_BOM,
    eBomBin.UTF8:     eBomCase.UTF8,
    eBomBin.UTF16_LE: eBomCase.UTF16_LE,
    eBomBin.UTF16_BE: eBomCase.UTF16_BE,
    eBomBin.UTF32_LE: eBomCase.UTF32_LE,
    eBomBin.UTF32_BE: eBomCase.UTF32_BE,
}

gBomCaseToFormatStr = {
    eBomCase.NO_BOM:   None,
    eBomCase.UTF8:     "utf_8",
    eBomCase.UTF16_LE: "utf_16_le",
    eBomCase.UTF32_LE: "utf_32_le",
    eBomCase.UTF16_BE: "utf_16_be",
    eBomCase.UTF32_BE: "utf_32_be"
}

#functions

#将扩展名字符串转化为扩展名列表
def ExtStrToExtList(s:str)->list:
    s = s.strip()            #将字符串前后空白移除
    s = s.replace(",", " ")  #将逗号替换为空格
    s = s.replace(";", " ")  #将分号替换为空格
    l = s.split()

    for e in l:
        if e == "":
            print("#错误：出现空扩展名！请检查由“-e”参数指定的扩展名字符串，或指定以使用默认值。")
            print("  程序当前版本的扩展名默认值为：“", gExtStr, "”")
            sys.exit(-1)
        elif e[0] != ".":
            print("#错误：出现并非由“.”起始的非法扩展名“", e, "”！请检查由“-e”参数指定的扩展名字符串，或指定以使用默认值。", sep="")
            print("  每个扩展名必须以“.”起始。例如：“.", e, "”。", sep="")
            print("  程序当前版本的扩展名默认值为：“", gExtStr, "”")
            sys.exit(-1)

    return l

#获取唯一字符串（等价字符串的唯一形式）
def GetUniqueStr(s:str)->str:
    global gUniqueArgMap
    return gUniqueArgMap[s] if s in gUniqueArgMap else s
	
def GetFileExt(FileFullPath:str)->str:
    return os.path.splitext(FileFullPath)[1]

def WalkFiles(walkDir:str)->list:
    global gArgs
    extStr  = gArgs["-e"]
    extList = ExtStrToExtList(extStr)
    dirBar  = "/"
    osStr   = platform.system()

    if walkDir == "":
        walkDir = "."
    
    if osStr == "Windows":
        dirBar  = "\\"
        walkDir = walkDir.replace("/", "\\")

    files = list()

    for dirPath, dirNames, fileNames in os.walk(walkDir):
        for fileName in fileNames:
            ext = GetFileExt(fileName)
            if ext in extList:
                fileFullName = dirPath + dirBar + fileName
                files.append(fileFullName)

    return files

def BomBinToBomCase(BOM_Bytes):
    global gBomBinToBomCase
    m = gBomBinToBomCase

    if BOM_Bytes in m:
        return m[BOM_Bytes]
    else:
        print("#错误：无法识别的BOM二进制内容。")
        sys.exit(-1)

def BomCaseToFormatStr(bomCase):
    global gBomCaseToFormatStr
    m = gBomCaseToFormatStr

    if bomCase in m:
        return m[bomCase]
    else:
        return None

def ResolveFileBin(fileBinContent:bytes)->dFileContent:

    for BOM_Bytes in eBomBin.enums():
        BomLen = len(BOM_Bytes)
        if fileBinContent[0:BomLen] == BOM_Bytes: #BOM匹配
            bomCase = BomBinToBomCase(BOM_Bytes)
            return dFileContent(
                bomCase,
                BOM_Bytes,
                BomCaseToFormatStr(bomCase),
                fileBinContent[BomLen:]
            )

    return None

def GetFileContent(s:str):
    f = open(s, "rb")
    fileBin = f.read()
    content = ResolveFileBin(fileBin)
    f.close()
    return content

def TranscodeBin(BinArray:bytes, SrcEncoding:str, DestEncoding:str)->bytes:
    s = BinArray.decode(SrcEncoding)
    return s.encode(DestEncoding)

def ConvertFile(s:str)->bool:
    dstFmStr = gArgs["-d"]
    content  = GetFileContent(s)
    try:
        newBin = TranscodeBin(content.memBin, content.formatStr, dstFmStr)
    except Exception as e:
        print("#错误：编解码时发生错误！")
        print("#提示：请放心，发生编解码错误的文件不会被修改。")
        print("  文件：“", s, "”", sep="")
        print("  错误信息：", e, sep="")
        return False #只要转换期出现异常，目标文件就不会被修改，因此是安全的。
    else:
        f = open(s, "wb") #将内容写入
        f.write(newBin)
        f.close()
    return True

def GetFiles()->list:
    global gArgs
    files = None
    isf = os.path.isfile
    isd = os.path.isdir
    dst = gArgs["-f"]
    
    if isf(dst):
        files = list()
        files.append(dst)
    elif isd(dst):
        files = WalkFiles(dst)

    return files

def Work():
    files    = GetFiles()
    contents = list()

    print("#消息：\r\n以下文件将被处理：")
    print("............................")
    for f in files:
        content = GetFileContent(f)
        contents.append(content)
        print("文件：“", f, "”", sep="")
        print("   BOM：", eBomCase.names(content.bomCase), "\t格式：", content.formatStr, 
            "（该格式由您指定）" if content.bomCase == eBomCase.NO_BOM else "",
            sep="")
    print("............................")
    print("共计：", len(files), " 个文件。\r\n", sep="")
    print("其中：")

    nNoBom, nBomUtf8 = 0, 0
    nBomUtf16LE, nBomUtf16BE = 0, 0
    nBomUtf32LE, nBomUtf32BE = 0, 0
    for c in contents:
        match c.bomCase:
            case eBomCase.NO_BOM:
                nNoBom += 1
            case eBomCase.UTF8:
                nBomUtf8 += 1
            case eBomCase.UTF16_LE:
                nBomUtf16LE += 1
            case eBomCase.UTF16_BE:
                nBomUtf16BE += 1
            case eBomCase.UTF32_LE:
                nBomUtf32LE += 1
            case eBomCase.UTF32_BE:
                nBomUtf32BE += 1
    
    if nNoBom != 0:
        print("   无BOM ", gArgs["-s"], "（该格式由您指定）文件数：", nNoBom, sep="")
    if nBomUtf8 != 0:
        print("   UTF-8 with BOM 文件数：", nBomUtf8, sep="")
    if nBomUtf16LE != 0:
        print("   UTF-16 LE with BOM 文件数：", nBomUtf16LE, sep="")
    if nBomUtf16BE != 0:
        print("   UTF-16 BE with BOM 文件数：", nBomUtf16BE, sep="")
    if nBomUtf32LE != 0:
        print("   UTF-32 LE with BOM 文件数：", nBomUtf32LE, sep="")
    if nBomUtf32BE != 0:
        print("   UTF-32 BE with BOM：", nBomUtf32BE, sep="")
    print()
    s = input("#继续？[y]是 [n]否：").strip().lower()

    if s != "y":
        print("#消息：您取消了这次任务，程序退出。")
        sys.exit(0)
    
    nBad = 0
    for f in files:
        if ConvertFile(f) is False:
            nBad += 1
    
    if nBad == 0:
        print("#消息：所有文件均已成功转换，程序结束。")
    else:
        print("#消息：",  len(files) - nBad, 
            "个文件转换成功，", nBad, "个文件转换失败，程序结束。")
    return

#初始化参数
def InitArgs():
    global gArgs
    global gArgMap
    global gBomCaseToFormatStr

    n, nMax = 1, len(sys.argv) #参数应从第2个参数开始。
    arg, s = None, None
    
    if nMax == 1:
        gArgs["-h"] = True
        gArgs["-v"] = False
        return

    while n < nMax:
        arg = sys.argv[n]
        s   = GetUniqueStr(arg)
        if s in gArgMap:
            e = gArgMap[s]
            if e == eArgSingle:
                gArgs[s] = True
            elif e == eArgDouble:
                n += 1
                if n < nMax:
                    gArgs[s] = sys.argv[n]
                else:
                    print("#错误：复合参数“", arg, "”后没有指定参数值。")
                    sys.exit(-1)
            else:
                print("#错误：无效的参数类型枚举值。")
                sys.exit(-1)
        else:
            print("#错误：参数“", arg,"”未定义。")
            sys.exit(-1)
        n += 1
    gBomCaseToFormatStr[eBomCase.NO_BOM] = gArgs["-s"] #这时将全局转换表的第一项改为设定的值。
    return
        

def GetVersion():
    global gVersion
    sVersion = "v" + gVersion
    print("\r\n#ubom版本：" + sVersion + "\r\n")

def GetHelp():
    if gArgs["-v"] == True:
        GetVersion()
    sHelp = \
'''
#信息：
  -h /? --help     帮助。
  -v    --version  显示版本号。

#参数：
  -f --file          文件（也可传入目录，内部自动进行判断）
  -s --source_format 源文件格式（format if no bom），默认为gb2312。
  -d --dest_format   目标文件格式（destination format），默认为utf_8_sig。
  -e --extentions    扩展名筛选，有一个默认的扩展名集合。

#用法Eg：
  ubom -f "C:/Code/" -s "gb2312"
  ubom -f "C:/Code/" -s "gb2312" -d "utf_8_sig" -e ".txt, .c, .h, .cpp, .hpp, .py, .pyw, .d, .nim"

#说明：
  使用前请务必自行备份目标文件（夹）！
  Be sure to back up the target file (folder) before use!
  使用前请务必自行备份目标文件（夹）！
  Be sure to back up the target file (folder) before use!
  使用前请务必自行备份目标文件（夹）！
  Be sure to back up the target file (folder) before use!
  程序已经过部分测试，尚未完全测试（所以备份是绝对必要的）。
  对于出现编解码错误的文件，程序将返回错误信息并直接跳过，不会作任何修改。
  “-d”与“-s”参数使用的字符串格式即Python直接支持的格式。
  详见：https://docs.python.org/zh-cn/3/library/codecs.html
  “-e”参数的分隔符支持“,”、“;”、空格与制表符。所有分隔符可以混合使用。
  例如Eg：
    ubom -f "C:/Code/" -s "gb2312" -d "utf_8_sig" -e ".txt, .c;.h,  .cpp .hpp;.py,.pyw,     .d  ;.nim"
'''
    print(sHelp)
    
def SelectProc():
    if gArgs["-h"] is True:
        return GetHelp
    if gArgs["-v"] is True:
        return GetVersion
    else:
        if gArgs["-s"] is None:
            print("#错误：为安全起见，请通过“-s”参数手动指定无BOM文件的文件格式。")
            sys.exit(-1)
        return Work

#主函数
def main():
    global gArgs
    InitArgs()
    SelectProc()()

main()
