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

from EmitCode import CodeEmitter
      
class StateMachineEmitter(object):
    def __init__(self, code, formatter, dfa_ir, section_id):
        self.code = code
        self.formatter = formatter
        self.dfa_ir = dfa_ir
        self.section_id = section_id
        
        # Shortcuts
        self.dfa = dfa_ir[section_id].dfa
        self.priority = dfa_ir[section_id].priority
        self.rules = dfa_ir.rules
        self.start_state = self.dfa.start_state
        setattr(self, 'block', self.code.block.__get__(self.code))
        setattr(self, 'line', self.code.line.__get__(self.code))
        
    def generate_state_machine(self):
        """
        Generate a function representing a DFA section in the 
        lexical analyzer
        """
        # Emit overall section DFA function
        method_name = self.formatter.get_token_method_name(self.section_id)
        token_type = self.formatter.get_token_type()
        with self.block("Function {method_name}() As {token_type}".format(method_name=method_name, token_type=token_type), "End Function"):
            self.generate_state_enum()
            start_state_id = self.formatter.get_state_id(self.start_state)
            self.line("Dim State As State = {state_id}".format(state_id=start_state_id)
            self.line("Dim Text As Poodle.Unicode.Text")
            with self.block("Do", "Loop"):
                self.line("Dim Capture As Integer = 0")
                with self.block("Select Case State", "End Select"):
                    for i, state in enumerate(self.dfa):
                        if i != 0:
                            self.line()
                        self.generate_state_case(state)
                self.line("If Capture = 1 Then Text.Append(This.Character)")
                self.line("This.Character = This.Stream->GetCharacter()")

    def generate_state_enum(self):
        """
        Generate an enum value for each state
        """
        with self.block("Enum State", "End Enum"):
            for id in sorted([self.formatter.get_state_id(state) for state in self.dfa]):
                self.line(id)        

    def generate_state_case(self, state):
        """
        Emits the case for a single state
        """
        self.line("Case {state_id}" % (state_id=self.formatter.get_state_id(state)))
        with self.block("Select Case This.Character", "End Select"):
            self.generate_transition_table(state)
            
            # else case (return token if in a final state)
            self.line("Case Else")
            if len(state.final_ids) > 0:
                self.generate_token_return_case(state)
            else:
                self.line("Text.Append(This.Character)")
                self.line("This.Character = This.Stream->GetCharacter()")
                self.line("Return {token_type}({token_id}, Text)".format(
                    token_type = self.formatter.get_token_type(),
                    token_id = self.formatter.get_token_id('InvalidCharacter')))

    def generate_transition_table(self, state):
        """
        Emit transitions to other states for a single character input
        """
        found_zero = False
        # Emit transition table
        for destination, edges in state.edges.iteritems():
            self.line("Case %s" % ", ".join([self.format_case(i) for i in edges]))
            if state == self.dfa_ir.sections[self.section].dfa.start_state:
                if 0 in zip(*iter(edges))[0]:
                    # Since 0 could mean either end of stream or a binary zero, use IsEndOfStream() to determine
                    found_zero = True
                    self.generate_check_zero_or_eof(invalid_otherwise=False)
            rules = [rule for id, rule in self.dfa_ir.rules.items() if id in destination.ids]
            if any([rule.has_action('capture') for rule in rules]):
                self.line("Capture = 1")
            self.line("State = {state_id}".format(state_id=self.formatter.get_state_id(destination)))
            self.line()
        if state == self.section.dfa.start_state and not found_zero:
            self.line("Case 0")
            self.generate_check_zero_or_eof(invalid_otherwise=True)
            self.line()
                    
    def format_case(self, range):
        """
        Format a case argument depending on if the range covers multiple values
        
        @return: the range formatted as an argument to "Case"
        """
        if range[0] == range[1]:
            return "%d" % range[0]
        else:
            return "%d To %d" % range
    
    def generate_check_zero_or_eof(self, invalid_otherwise):
        """
        Emit a block that checks for special characters
        """
        with self.block("If Stream->IsEndOfStream() Then", "End If"):
            self.line("Return {token_type}({token_id}, Poodle.Unicode.Text())" % (
                self.formatter.get_token_type(), 
                self.formatter.get_token_id('EndOfStream')))
            if invalid_otherwise:
                self.continue_block("Else")
                self.line("Return {token_type}({token_id}, Text)".format(
                    self.formatter.get_token_type(), 
                    self.formatter.get_token_id('InvalidCharacter')))

    def generate_token_return_case(self, state):
        token = min(state.final_ids, key = lambda x: self.priority.index(x))
        rule = self.rules[token]
        if rule.action is not None and rule.action.lower() == 'skip':
            # Reset state machine if token is skipped
            self.line("State = {state_id}".format(state_id = start_state))
            self.line("Text = Poodle.Unicode.Text()")
            self.line("Continue Do")
        else:
            section_action, section_id = rule.section_action
            if section_action.lower() == 'enter':
                self.line('This.EnterSection({namespace}.{section_id}Section)'.format( 
                    namespace=namespace,
                    section_id=self.formatter.get_section_id(section_id))
            elif section_action.lower() == 'exit':
                self.line('This.ExitSection()')
            if rule.action is not None and rule.action.lower() == 'capture':
                text="Text"
            else:
                text="Poodle.Unicode.Text()"
            self.line("Return {token_type}(token_id}, {text})".format(
                token_type = self.formatter.get_token_type(),
                token_id = self.formatter.get_token_id(rule),
                text=text))
            