# Copyright (C) 2014 Parker Michaels
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import os
import os.path
import re
import sys
import StringIO
import collections
import itertools
from EmitCode import CodeEmitter
from FileTemplate import FileTemplate
from PluginTemplate import PluginTemplate

def create_emitter(lexical_analyzer, plugin_files_directory, output_directory, plugin_options):
    return FreeBasicEmitter(lexical_analyzer, plugin_files_directory, output_directory, plugin_options)

class FreeBasicEmitter(PluginTemplate):
    """
    Emits a lexical analyzer as FreeBasic source code.
    @ivar lexical_analyzer: the lexical analyzer to emit
    @ivar ids: a dict mapping states to an enum element in the FreeBasic source
    @ivar dfa: the deterministic finite automata (DFA) representing the lexical analyzer.
    """
    reserved_keywords = set([
        "__date__", "__date_iso__", "__fb_argc__", "__fb_argv__", 
        "__fb_backend__", "__fb_bigendian__", "__fb_build_date__", 
        "__fb_cygwin__", "__fb_darwin__", "__fb_debug__", "__fb_dos__", 
        "__fb_err__", "__fb_fpmode__", "__fb_fpu__", "__fb_freebsd__", 
        "__fb_gcc__", "__fb_lang__", "__fb_linux__", "__fb_main__", 
        "__fb_min_version__", "__fb_mt__", "__fb_netbsd__", "__fb_openbsd__", 
        "__fb_option_byval__", "__fb_option_dynamic__", "__fb_option_escape__", 
        "__fb_option_explicit__", "__fb_option_gosub__", 
        "__fb_option_private__", "__fb_out_dll__", "__fb_out_exe__", 
        "__fb_out_lib__", "__fb_out_obj__", "__fb_pcos__", "__fb_signature__", 
        "__fb_sse__", "__fb_unix__", "__fb_vectorize__", "__fb_ver_major__", 
        "__fb_ver_minor__", "__fb_ver_patch__", "__fb_version__", 
        "__fb_win32__", "__fb_xbox__", "__file__", "__file_nq__", 
        "__function__", "__function_nq__", "__line__", "__path__", "__time__", 
        "assert", "define", "else", "elseif", "endif", "endmacro", "error", 
        "if", "ifdef", "ifndef", "inclib", "include", "lang", "libpath", "line", 
        "macro", "pragma", "print", "undef", "dynamic", "static", "abs", 
        "abstract", "access", "acos", "add", "alias", "allocate", "alpha", 
        "and", "andalso", "any", "append", "as", "assertwarn", "asc", "asin", 
        "asm", "atan2", "atn", "base", "beep", "bin", "binary", "bit", 
        "bitreset", "bitset", "bload", "bsave", "byref", "byte", "byval", 
        "call", "callocate", "case", "cast", "cbyte", "cdbl", "cdecl", "chain", 
        "chdir", "chr", "cint", "circle", "class", "clear", "clng", "clngint", 
        "close", "cls", "color", "command", "common", "condbroadcast", 
        "condcreate", "conddestroy", "condsignal", "condwait", "const", 
        "constructor", "continue", "cos", "cptr", "cshort", "csign", "csng", 
        "csrlin", "cubyte", "cuint", "culng", "culngint", "cunsg", "curdir", 
        "cushort", "custom", "cvd", "cvi", "cvl", "cvlongint", "cvs", "cvshort", 
        "data", "date", "dateadd", "datediff", "datepart", "dateserial", 
        "datevalue", "day", "deallocate", "declare", "defbyte", "defdbl", 
        "defined", "defint", "deflng", "deflongint", "defshort", "defsng", 
        "defstr", "defubyte", "defuint", "defulongint", "defushort", "delete", 
        "destructor", "dim", "dir", "do", "loop", "double", "draw", "dylibfree", 
        "dylibload", "dylibsymbol", "encoding", "end", "enum", "environ", "eof", 
        "eqv", "erase", "erfn", "erl", "ermn", "err", "exec", "exepath", "exit", 
        "exp", "export", "extends", "extern", "field", "fileattr", "filecopy", 
        "filedatetime", "fileexists", "filelen", "fix", "flip", "for", "next", 
        "format", "frac", "fre", "freefile", "function", "get", "getjoystick", 
        "getkey", "getmouse", "gosub", "goto", "hex", "hibyte", "hiword", 
        "hour", "then", "iif", "imageconvertrow", "imagecreate", "imagedestroy", 
        "imageinfo", "imp", "implements", "import", "inkey", "inp", "input", 
        "input$", "instr", "instrrev", "int", "integer", "is", "isdate", "kill", 
        "lbound", "lcase", "left", "len", "let", "lib", "lobyte", "loc", 
        "local", "locate", "lock", "lof", "log", "long", "longint", "loword", 
        "lpos", "lprint", "lset", "ltrim", "mid", "minute", "mkd", "mkdir", 
        "mki", "mkl", "mklongint", "mks", "mkshort", "mod", "month", 
        "monthname", "multikey", "mutexcreate", "mutexdestroy", "mutexlock", 
        "mutexunlock", "naked", "name", "namespace", "new", "not", "now", 
        "object", "oct", "offsetof", "on", "once", "open", "operator", 
        "option", "option", "or", "orelse", "out", "output", "overload", 
        "override", "paint", "palette", "pascal", "pcopy", "peek", "pmap", 
        "point", "pointcoord", "pointer", "poke", "pos", "preserve", "preset", 
        "private", "procptr", "property", "protected:", "pset", 
        "ptr", "public", "put", "random", "randomize", "read", 
        "reallocate", "redim", "rem", "reset", "restore", "resume", "return", 
        "rgb", "rgba", "right", "rmdir", "rnd", "rset", "rtrim", "run", "sadd", 
        "scope", "screen", "screencopy", "screencontrol", "screenevent", 
        "screeninfo", "screenglproc", "screenlist", "screenlock", "screenptr", 
        "screenres", "screenset", "screensync", "screenunlock", "second", 
        "seek", "select", "setdate", "setenviron", "setmouse", "settime", "sgn", 
        "shared", "shell", "shl", "shr", "short", "sin", "single", "sizeof", 
        "sleep", "space", "spc", "sqr", "stdcall", "step", "stick", "stop", 
        "str", "strig", "string", "strptr", "sub", "swap", "system", "tab", 
        "tan", "this", "threadcall", "threadcreate", "threadwait", "time", 
        "timeserial", "timevalue", "timer", "to", "trans", "trim", "type", 
        "typeof", "ubound", "ubyte", "ucase", "uinteger", "ulong", "ulongint", 
        "union", "unlock", "unsigned", "until", "ushort", "using", "va_arg", 
        "va_first", "va_next", "val", "vallng", "valint", "valuint", "valulng", 
        "var", "varptr", "view", "virtual", "wait", "wbin", "wchr", "weekday", 
        "weekdayname", "wend", "while", "whex", "width", "window", 
        "windowtitle", "winput", "with", "woct", "write", "wspace", "wstr", 
        "wstring", "xor", "year", "zstring" 
    ])
    bi_file = "LexicalAnalyzer.bi"
    bas_file = "LexicalAnalyzer.bas"
    demo_file = os.path.join("Demo", "Demo.bas")
    windows_makefile = os.path.join("Demo", "make_demo.bat")
    linux_makefile = os.path.join("Demo", "make_demo.sh")
    class_name = "LexicalAnalyzer"
    namespace = "Poodle"
    
    def __init__(self, lexical_analyzer, plugin_files_directory, output_directory, plugin_options):
        """
        @param lexical_analyzer: LexicalAnalyzer object representing the lexical analyzer to emit as FreeBasic code.
        @param plugin_files_directory: string specifying the location of template files
        @param output_directory: string specifying the directory where output files should be emitted
        """
        self.lexical_analyzer = lexical_analyzer
        self.plugin_files_directory = plugin_files_directory
        self.output_directory = output_directory
        self.ids = {}
        self.rule_ids = {}
        self.dfa = None
        self.plugin_options = plugin_options
    
    # Public interface
    def emit(self):
        """
        Emits the lexical analyzer as a FreeBasic header file and source file.
        """
        if not self.lexical_analyzer.is_finalized():
            self.lexical_analyzer.finalize()
        self.dfa = self.lexical_analyzer.get_min_dfa()
        self.map_state_ids()
        self.map_rule_names()
        
        # Emit lexical analyzer header
        bi_template_file = os.path.join(self.plugin_files_directory, FreeBasicEmitter.bi_file)
        bi_output_file = os.path.join(self.output_directory, self.get_class_name() + ".bi")
        for stream, token, indent in FileTemplate(bi_template_file, bi_output_file):
            if token == 'ENUM_TOKEN_IDS':
                token_ids = [self.rule_ids[rule.id.title()] for rule in self.lexical_analyzer.rules]
                token_ids.extend([self.rule_ids[id.title()] for id in self.lexical_analyzer.reserved_ids])
                for id in token_ids:
                    stream.write(" "*indent + id + "\n")
            elif token == "CLASS_NAME":
                stream.write(self.get_class_name())
            elif token == "HEADER_GUARD_NAME":
                stream.write("POODLE_%s_BI" % self.get_class_name().upper())
            elif token == "TOKEN_IDNAMES_LIMIT":
                stream.write(str(len(self.rule_ids)+1))
            else:
                raise Exception('Unrecognized token in header template: "%s"' % token)
        
        # Emit lexical analyzer source
        bas_template_file = os.path.join(self.plugin_files_directory, FreeBasicEmitter.bas_file)
        bas_output_file = os.path.join(self.output_directory, self.get_class_name() + ".bas")
        for stream, token, indent in FileTemplate(bas_template_file, bas_output_file):
            if token == 'ENUM_STATE_IDS':
                for state_id in sorted(list(self.ids.values())):
                    stream.write(" "*indent + state_id + '\n')
            elif token == 'INITIAL_STATE':
                stream.write(self.ids[self.dfa.start_state])
            elif token == 'CLASS_NAME':
                stream.write(self.get_class_name())
            elif token == 'STATE_MACHINE':
                self.generate_state_machine(stream, indent)
            elif token == "TOKEN_IDNAMES_LIMIT":
                stream.write(str(len(self.rule_ids)+1))
            elif token == "TOKEN_IDNAMES":
                rule_id_list = [rule.id for rule in self.lexical_analyzer.rules]
                rule_id_list.extend(self.lexical_analyzer.reserved_ids)
                formatted_ids = ", _\n".join(" "*indent + "@\"%s\"" % rule_id for rule_id in rule_id_list)
                stream.write(formatted_ids + "_ \n")
            else:
                raise Exception('Unrecognized token in source template: "%s"' % token)

        # Emit demo files
        for support_file in [
            FreeBasicEmitter.demo_file,
            FreeBasicEmitter.windows_makefile,
            FreeBasicEmitter.linux_makefile
        ]:
            support_template_file = os.path.join(self.plugin_files_directory, support_file)
            support_output_file = os.path.join(self.output_directory, support_file)
            for stream, token, indent in FileTemplate(support_template_file, support_output_file):
                if token == 'CLASS_NAME':
                    stream.write(self.get_class_name())
                
    def get_class_name(self):
        class_name = self.plugin_options.class_name
        if class_name is None:
            class_name = FreeBasicEmitter.default_class_name
        if re.match("[A-Za-z_][A-Za-z0-9_]*", class_name) is None:
            raise Exception("Invalid class name '%s'" % class_name)
        elif class_name in FreeBasicEmitter.reserved_keywords:
            raise Exception("Class name '%s' is reserved" % class_name)
        return class_name
                
    def get_output_directories(self):
        return [os.path.join(*i) for i in [
            ("Demo",),
            ("Stream",),
            ("Stream", "Windows"),
            ("Stream", "Linux")
        ]]
        
    def get_files_to_copy(self):
        return [os.path.join(*i) for i in [
            ("Stream", "Windows", "MemoryMapWindows.bas"),
            ("Stream", "Windows", "MemoryMapWindows.bi"),
            ("Stream", "Linux", "MemoryMapLinux.bas"),
            ("Stream", "Linux", "MemoryMapLinux.bi"),
            ("Stream", "ASCIIStream.bas"),
            ("Stream", "ASCIIStream.bi"),
            ("Stream", "CharacterStream.bas"),
            ("Stream", "CharacterStream.bi"),
            ("Stream", "CharacterStreamFromFile.bas"),
            ("Stream", "CharacterStreamFromFile.bi"),
            ("Stream", "MemoryMap.bas"),
            ("Stream", "MemoryMap.bi"),
            ("Stream", "Unicode.bas"),
            ("Stream", "Unicode.bi"),
            ("Stream", "UnicodeConstants.bas"),
            ("Stream", "UnicodeConstants.bi"),
            ("Stream", "UTF8Stream.bas"),
            ("Stream", "UTF8Stream.bi"),
            ("Stream", "UTF16Stream.bas"),
            ("Stream", "UTF16Stream.bi"),
            ("Stream", "UTF32Stream.bas"),
            ("Stream", "UTF32Stream.bi")
        ]]
               
    # Private files
    def map_state_ids(self):
        """
        Maps all states to an enum element in the FreeBasic source code.
        """
        self.ids[self.dfa.start_state] = "InitialState"
        for state in self.dfa:
            if state != self.dfa.start_state:
                initial_id = "".join([i.title() for i in sorted(list(state.ids))])[:64]
                id = initial_id
                n = 1
                while id in self.ids.values() or id.lower() in FreeBasicEmitter.reserved_keywords:
                    id_prefix = initial_id[:64-len(str(n))]
                    id = "%s%d" % (id_prefix, n)
                    n += 1
                self.ids[state] = id
                
    def map_rule_names(self):
        """
        Maps all rule names to an enum element in the FreeBasic source code
        """
        all_ids = [rule.id.title() for rule in self.lexical_analyzer.rules]
        all_ids.extend([id.title() for id in self.lexical_analyzer.reserved_ids])
        for id in all_ids:
            n = 1
            code_id = id[:64]
            while code_id in self.rule_ids.values() or code_id.lower() in FreeBasicEmitter.reserved_keywords:
                prefix = id[:64-len(str(n))]
                code_id = '%s%d' % (prefix, n)
                n += 1
            self.rule_ids[id] = code_id
        
    def generate_state_machine(self, stream, indent):
        """
        Generates a state machine in FreeBasic source code represented by two tiers of "Select Case" statemenets.
        @param stream: a Python file object to which the state machine should be written
        @param indent: the number of spaces by which the code should be indented.
        """
        code = CodeEmitter(stream)
        for i in xrange(indent/4):
            code.indent()
        
        for i, state in enumerate(self.dfa):
            if i != 0:
                code.line()
            code.line("Case Poodle.%s" % self.ids[state])
            code.line("Select Case This.Character")
            code.indent()
            
            def ranges(i):
                for a, b in itertools.groupby(enumerate(i), lambda (x, y): y - x):
                    b = list(b)
                    yield b[0][1], b[-1][1]
            
            def format_case(range):
                if range[0] == range[1]:
                    return "%d" % range[0]
                else:
                    return "%d To %d" % range
            
            def emit_check_zero(invalid_otherwise):
                code.line("If Stream->IsEndOfStream() Then")
                code.indent()
                code.line("Return Poodle.Token(Poodle.Token.EndOfStream, Poodle.Unicode.Text())")
                code.dedent()
                if invalid_otherwise:
                    code.line("Else")
                    code.indent()
                    code.line("Return Poodle.Token(Poodle.Token.InvalidCharacter, Text)")
                    code.dedent()
                code.line("End If")
                
            found_zero = False
            for destination, edges in state.edges.iteritems():
                code.line("Case %s" % ", ".join([format_case(i) for i in edges]))
                if state == self.dfa.start_state:
                    if 0 in zip(*iter(edges))[0]:
                        # Since 0 could mean either end of stream or a binary zero, use IsEndOfStream() to determine
                        found_zero = True
                        emit_check_zero(invalid_otherwise=False)
                rules = [rule for rule in self.lexical_analyzer.rules if rule.id in destination.ids]
                if any([rule.action is not None and rule.action.lower() == 'capture' for rule in rules]):
                    code.line("Capture = 1")
                code.line("State = Poodle.%s" % self.ids[destination])
                code.line()
            
            if state == self.dfa.start_state and not found_zero:
                code.line("Case 0")
                emit_check_zero(invalid_otherwise=True)
                code.line()
            
            # else case (return token if in final state
            code.line("Case Else")
            if len(state.final_ids) > 0:
                tokens_by_priority = [rule.id for rule in self.lexical_analyzer.rules]
                token = min(state.final_ids, key = lambda x: tokens_by_priority.index(x)).title()
                rule = [rule for rule in self.lexical_analyzer.rules if rule.id.title() == token][0]
                if rule.action is not None and rule.action.lower() == 'skip':
                    # Reset state machine if token is skipped
                    code.line("State = Poodle.%s" % self.ids[self.dfa.start_state])
                    code.line("Text = Poodle.Unicode.Text()")
                    code.line("Continue Do")
                elif rule.action is not None and rule.action.lower() == 'capture':
                    code.line("Return Poodle.Token(Poodle.Token.%s, Text)" % self.rule_ids[token])
                else:
                    code.line("Return Poodle.Token(Poodle.Token.%s, Poodle.Unicode.Text())" % self.rule_ids[token])
            else:
                code.line("Text.Append(This.Character)")
                code.line("This.Character = This.Stream->GetCharacter()")
                code.line("Return Poodle.Token(Poodle.Token.InvalidCharacter, Text)")
            
            code.dedent()
            code.line("End Select")
