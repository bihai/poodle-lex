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
        self.section = self.dfa_ir.sections[section_id]
        self.dfa = self.section.dfa
        self.rules = self.section.rules
        self.inherits = self.section.inherits
        self.exits = self.section.exits
        self.parent = self.section.parent
        self.ids = dfa_ir.rule_ids
        self.start_state = self.dfa.start_state
        
        setattr(self, 'block', self.code.block.__get__(self.code))
        setattr(self, 'line', self.code.line.__get__(self.code))
        setattr(self, 'continue_block', self.code.continue_block.__get__(self.code))
        self.state_id_formatter = self.formatter.get_state_id_formatter(self.rules)
        setattr(self, 'get_state_id', self.state_id_formatter.get_state_id)
        setattr(self, 'add_state_id', self.state_id_formatter.add_state_id)
     
    @staticmethod
    def generate_state_machine_switch(code, formatter, dfa_ir):
        method_name = formatter.get_state_machine_method_name(None, is_relative=False)
        token_type = formatter.get_type('token', is_relative=False)
        with code.block("Function {method_name}() As {token_type}".format(method_name=method_name, token_type=token_type), "End Function"):
            code.line("Dim ScannedToken As {token_type}".format(token_type=token_type))
            with code.block("Do", "Loop While ScannedToken.Id = {token_type}.{id}".format(
                token_type=formatter.get_type('token', is_relative=True),
                id=formatter.get_token_id('SkippedToken'))):
                with code.block("Select Case This.Mode", "End Select"):
                    for i, section in enumerate(dfa_ir.sections):
                        if i != 0:
                            code.line()
                        if i == len(dfa_ir.sections)-1:
                            code.line("Case Else")
                        else:
                            code.line("Case {section}".format(section=formatter.get_section_id(section)))
                        method_name = formatter.get_state_machine_method_name(section, is_relative=True)
                        code.line("ScannedToken = This.{method_name}()".format(method_name=method_name))
            code.line("Return ScannedToken")
        
    def generate_state_machine(self):
        """
        Generate a function representing a DFA section in the 
        lexical analyzer
        """
        # Emit overall section DFA function
        if len(self.dfa_ir.sections) > 1:
            id = self.section_id
        else:
            id = None
        method_name = self.formatter.get_state_machine_method_name(id, is_relative=False)
        token_type = self.formatter.get_type('token', is_relative=False)
        self.add_state_id(self.start_state, 'InitialState')
            
        with self.block("Function {method_name}() As {token_type}".format(method_name=method_name, token_type=token_type), "End Function"):
            self.generate_state_enum()
            start_state_id = self.get_state_id(self.start_state)
            self.line("Dim State As StateMachineState = {scope}.{state_id}".format(scope="StateMachineState", state_id=start_state_id))
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
        with self.block("Enum StateMachineState", "End Enum"):
            for state in self.dfa:
                self.line(self.get_state_id(state))
                
    def generate_state_case(self, state):
        """
        Emits the case for a single state
        """
        self.line("Case {scope}.{state_id}".format(scope="StateMachineState", state_id=self.get_state_id(state)))
        with self.block("Select Case This.Character", "End Select"):
            self.generate_transition_table(state)
            
            # else case (return token if in a final state)
            self.line("Case Else")
            if len(state.final_ids) > 0:
                self.generate_token_return_case(state)
            else:
                if state == self.start_state and (self.exits or self.inherits):
                    # Sections can have special behavior for if the first character does not match
                    if self.exits:
                        self.line('This.ExitSection()')
                    if self.inherits:
                        method_name = self.formatter.get_state_machine_method_name(self.parent, is_relative=True)
                        self.line("Return This.{method_name}()".format(method_name=method_name))
                    elif self.exits:
                        # Need to return something to skip the token and avoid an error
                        self.line("Return {token_type}({token_type}.{token_id}, Unicode.Text())".format(
                            token_type = self.formatter.get_type('token', is_relative=False),
                            token_id=self.formatter.get_token_id('SkippedToken')))
                else:
                    self.line("Text.Append(This.Character)")
                    self.line("This.Character = This.Stream->GetCharacter()")
                    self.line("Return {token_type}({token_type}.{token_id}, Text)".format(
                        token_type = self.formatter.get_type('token', is_relative=False),
                        token_id = self.formatter.get_token_id('InvalidCharacter')))

    def generate_transition_table(self, state):
        """
        Emit transitions to other states for a single character input
        """
        found_zero = False
        
        
        # Emit transition table
        for destination, edges in state.edges.iteritems():
            self.line("Case %s" % ", ".join([self.format_case(i) for i in edges]))
            if state == self.start_state:
                if 0 in zip(*iter(edges))[0]:
                    # Since 0 could mean either end of stream or a binary zero, use IsEndOfStream() to determine
                    found_zero = True
                    self.generate_check_zero_or_eof(invalid_otherwise=False)
            rules = [rule for rule in self.rules if rule.id in destination.ids]
            if any('capture' in rule.action for rule in rules):
                self.line("Capture = 1")
            self.line("State = {scope}.{state_id}".format(scope="StateMachineState", state_id=self.get_state_id(destination)))
            self.line()
        if state == self.start_state and not found_zero:
            self.line("Case 0")
            self.generate_check_zero_or_eof(invalid_otherwise=True)
            self.line()
                    
    def format_case(self, range):
        """
        Format a case argument depending on if the range covers multiple values
        @return: the range formatted as an argument to "Case"
        """
        if range[0] == range[1]:
            return str(range[0])#self.formatter.get_unicode_char_name(range[0])
        else:
            return str(range[0]) + " to " + str(range[1])
            #"{minv} To {maxv}".format(
                #minv = self.formatter.get_unicode_char_name(range[0]), 
                #maxv = self.formatter.get_unicode_char_name(range[1]))
    
    def generate_check_zero_or_eof(self, invalid_otherwise):
        """
        Emit a block that checks for special characters
        """
        with self.block("If Stream->IsEndOfStream() Then", "End If"):
            self.line("Return {token_type}({token_type}.{token_id}, Poodle.Unicode.Text())".format(
                token_type=self.formatter.get_type('token', is_relative=False), 
                token_id=self.formatter.get_token_id('EndOfStream')))
            if invalid_otherwise:
                self.continue_block("Else")
                self.line("Return {token_type}({token_type}.{token_id}, Text)".format(
                    token_type=self.formatter.get_type('token', is_relative=False), 
                    token_id=self.formatter.get_token_id('InvalidCharacter')))

    def generate_token_return_case(self, state):
        # First rule with an ID in the state's final IDs takes priority
        rule = self.section.get_matching_rule(state)
        if rule is None:
            raise Exception("Internal error - unable to determine matching rule")

        # Switch sections if necessary
        section_action, section_id = rule.section_action
        if section_action is not None:
            if section_action in ('enter', 'switch'):
                self.line('This.{action}Section({namespace}.{class_name}.{section_id})'.format( 
                    action = section_action.title(),
                    namespace=self.formatter.get_namespace(),
                    class_name=self.formatter.get_mode_stack_class_name(),
                    section_id=self.formatter.get_section_id(section_id)))
            elif section_action == 'exit':
                self.line('This.ExitSection()')
           
        if 'skip' in rule.action:
            if len(self.dfa_ir.sections) > 1:
                # On multi-section lexers, we need to return a 'skipped' token
                self.line("Return {token_type}({token_type}.{token_id}, Unicode.Text())".format(
                    token_type = self.formatter.get_type('token', is_relative=False),
                    token_id=self.formatter.get_token_id('SkippedToken')))
            else:
                # On single-section lexers, we can just reset the state machine
                self.line("State = {scope}.{state_id}".format(scope="StateMachineState", state_id = self.get_state_id(self.start_state)))
                self.line("Text = Poodle.Unicode.Text()")
                self.line("Continue Do")
        else:
            if 'capture' in rule.action:
                text="Text"
            else:
                text="Poodle.Unicode.Text()"
            self.line("Return {token_type}({token_type}.{token_id}, {text})".format(
                token_type = self.formatter.get_type('token', is_relative=False),
                token_id = self.formatter.get_token_id(rule.name if rule.name is not None else 'Anonymous'),
                text=text))
