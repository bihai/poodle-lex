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
import copy
from EmitCode import CodeEmitter
from FileTemplate import FileTemplate
from PluginTemplate import PluginTemplate

def create_emitter(lexical_analyzer, dependencies, plugin_options):
    return FreeBasicEmitter(lexical_analyzer, dependencies, plugin_options)

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
    mode_bi_file = "ModeStack.bi"
    mode_bas_file = "ModeStack.bas"
    demo_file = os.path.join("Demo", "Demo.bas")
    windows_makefile = os.path.join("Demo", "make_demo.bat")
    linux_makefile = os.path.join("Demo", "make_demo.sh")
    default_class_name = "LexicalAnalyzer"
    poodle_namespace = "Poodle"
    default_namespace = poodle_namespace
    
    def __init__(self, lexical_analyzer, dependencies, plugin_options):
        """
        @param lexical_analyzer: DeterministicIR object representing the lexical analyzer to emit as FreeBasic code.
        @param depedencies: dict mapping string module identifiers of dependencies to Python module objects.
        @param plugin_options: LanguagePlugins.PluginOptions object containing options which affect the generation of code.
        """
        self.lexical_analyzer = lexical_analyzer
        self.plugin_options = copy.copy(plugin_options)
        self.VariableFormatter = dependencies["VariableFormatter"].VariableFormatter
        self.StateMachineEmitter = dependencies["StateMachine"].StateMachineEmitter
        self.ids = {}
        self.rule_ids = {}
        self.dfa = None

        # Process plugin options
        for name, description in [
            (plugin_options.class_name, 'Class name'),
            (plugin_options.file_name, 'Base file name'),
            (plugin_options.namespace, 'Namespace')
        ]:
            if name is not None:
                if re.match("[A-Za-z_][A-Za-z0-9_]*", name) is None:
                    raise Exception("Invalid {object} '{name}'".format(object=description.lower(), name=name))
                elif name.lower() in FreeBasicEmitter.reserved_keywords:
                    raise Exception("{object} '{name}' is reserved".format(object=description, name=name))
        
        if self.plugin_options.class_name is None:
            self.plugin_options.class_name = FreeBasicEmitter.default_class_name
        if self.plugin_options.file_name is None:
            self.plugin_options.file_name = self.plugin_options.class_name
        if self.plugin_options.namespace is None:
            self.plugin_options.namespace = FreeBasicEmitter.default_namespace
            
        self.formatter = self.VariableFormatter(
            plugin_options=self.plugin_options, 
            reserved_ids=self.reserved_keywords, 
            poodle_namespace=self.poodle_namespace)

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
            ("Stream", "UnicodeTextStream.bas"),
            ("Stream", "UnicodeTextStream.bi"),
            ("Stream", "UTF8Stream.bas"),
            ("Stream", "UTF8Stream.bi"),
            ("Stream", "UTF16Stream.bas"),
            ("Stream", "UTF16Stream.bi"),
            ("Stream", "UTF32Stream.bas"),
            ("Stream", "UTF32Stream.bi")
        ]]

    def get_files_to_generate(self):
        files = [
            (self.bi_file, self.plugin_options.file_name + ".bi"),
            (self.bas_file, self.plugin_options.file_name + ".bas"),
            (self.demo_file, self.demo_file),
            (self.windows_makefile, self.windows_makefile),
            (self.linux_makefile, self.linux_makefile)
        ]
        if len(self.lexical_analyzer.sections) > 1:
            files.extend((
                (self.mode_bi_file, self.plugin_options.file_name + "ModeStack.bi"),
                (self.mode_bas_file, self.plugin_options.file_name + "ModeStack.bas")
            ))
        return files
        
    def process(self, token):
        if token.token == 'BASE_CLASS':
            if len(self.lexical_analyzer.sections) > 1:
                token.stream.write(self.formatter.get_mode_stack_class_name())
            else:
                token.stream.write('Object')
        elif token.token == 'BASE_FILE_NAME':
            token.stream.write(self.plugin_options.file_name)
        elif token.token == 'CLASS_NAME':
            token.stream.write(self.formatter.get_class_name())
        elif token.token == 'DEFAULT_ENCODING':
            token.stream.write(self.formatter.get_default_encoding())
        elif token.token == 'ENUM_MODE_IDS':
            code = CodeEmitter(token.stream, token.indent)
            for section in self.lexical_analyzer.sections:
                x = self.formatter.get_section_id(section)
                code.line(x)
        elif token.token == 'ENUM_TOKEN_IDS':
            code = CodeEmitter(token.stream, token.indent)
            for rule in sorted(self.lexical_analyzer.rules):
                code.line(self.formatter.get_token_id(rule))
        elif token.token == 'HEADER_GUARD_NAME':
            token.stream.write('{namespace}_{class_name}_BI'.format(
                namespace = self.plugin_options.namespace.upper(),
                class_name = self.plugin_options.class_name.upper()))
        elif token.token == 'HEADER_GUARD_MODE_NAME':
            token.stream.write('{namespace}_{class_name}_BI'.format(
                namespace = self.plugin_options.namespace.upper(),
                class_name = self.formatter.get_mode_stack_class_name().upper()))
        elif token.token == 'INITIAL_MODE_ID':
            token.stream.write(self.formatter.get_section_id(('::main::',)))
        elif token.token == 'MODE_INCLUDE':
            if len(self.lexical_analyzer.sections) > 1:
                code = CodeEmitter(token.stream, token.indent)
                code.line('#include "{include_file}"'.format(include_file=self.plugin_options.file_name + "ModeStack.bi"))
        elif token.token == 'MODE_SOURCE':
            if len(self.lexical_analyzer.sections) > 1:
                token.stream.write(" ../{base_file_name}ModeStack.bas".format(base_file_name=self.plugin_options.file_name))
        elif token.token == 'MODE_STACK_CLASS_NAME':
            token.stream.write(self.formatter.get_mode_stack_class_name())
        elif token.token == 'NAMESPACE':
            token.stream.write(self.formatter.get_namespace())
        elif token.token == 'STACK_DEPTH_ID':
            token.stream.write('{namespace}_{class_name}_STACK_DEPTH'.format(
                namespace=self.plugin_options.namespace.upper(),
                class_name=self.formatter.get_mode_stack_class_name().upper()))
        elif token.token == 'STACK_DEPTH':
            token.stream.write('32')
        elif token.token == 'STATE_MACHINE_DECLARATIONS':
            if len(self.lexical_analyzer.sections) > 1:
                code = CodeEmitter(token.stream, token.indent)
                for section in self.lexical_analyzer.sections:
                    code.line("Declare Function {method_name}() As {token_type}".format(
                        method_name=self.formatter.get_state_machine_method_name(section, True),
                        token_type=self.formatter.get_type('token', True)))
        elif token.token == 'STATE_MACHINES':
            code = CodeEmitter(token.stream, token.indent)
            self.StateMachineEmitter.generate_state_machine_switch(code, self.formatter, self.lexical_analyzer)
            for i, section in enumerate(self.lexical_analyzer.sections):
                code.line()
                emitter = self.StateMachineEmitter(
                    code=code,
                    formatter=self.formatter,
                    dfa_ir=self.lexical_analyzer,
                    section_id=section)
                emitter.generate_state_machine()
        elif token.token == 'TOKEN_IDNAMES':
            code = CodeEmitter(token.stream, token.indent)
            for i, rule in enumerate(sorted(self.lexical_analyzer.rules)):
                template = '@"{name}"'
                template += ", _" if i < len(self.lexical_analyzer.rules)-1 else " _"
                code.line(template.format(name=rule))
        elif token.token == 'TOKEN_IDNAMES_LIMIT':
            token.stream.write(str(len(self.lexical_analyzer.rules)+1))
        elif token.token.startswith('TYPE_REL_'):
            type_name = token.token[len('TYPE_REL_'):].lower()
            token.stream.write(self.formatter.get_type(type_name, True))
        elif token.token.startswith('TYPE_'):
            type_name = token.token[len('TYPE_'):].lower()
            token.stream.write(self.formatter.get_type(type_name, False))
        else:
            raise Exception("Token '{id}' not recognized".format(id=token.token))
