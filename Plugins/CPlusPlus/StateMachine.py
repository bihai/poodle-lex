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

class StateMachineEmitter(object):
    def __init__(self, dfa_ir, section_id, formatter, emitter):
        self.section_id = section_id
        self.dfa_ir = dfa_ir
        self.formatter = formatter
        self.emitter = emitter
     
        # Shortcuts
        self.section = dfa_ir.sections[section_id]
        self.inherits = self.section.inherits
        self.parent = self.section.parent
        self.dfa = dfa_ir.sections[section_id].dfa
        self.start_state = self.dfa.start_state
        self.line = emitter.line.__get__(emitter)
        self.block = emitter.block.__get__(emitter)
        self.continue_block = emitter.continue_block.__get__(emitter)
        self.emit = emitter.emit.__get__(emitter)


        self.state_id_formatter = formatter.get_state_id_formatter(self.section.rules)
        self.get_state_id = self.state_id_formatter.get_state_id
        self.add_state_id = self.state_id_formatter.add_state_id
        self.add_state_id(self.start_state, "INITIAL_STATE")
        self.add_state_id('invalid_char_state', 'INVALID_CHAR_STATE')


    def emit_state_machine(self):
        section_id = self.section_id if len(self.dfa_ir.sections) > 1 else ''
        self.line("{token_type} {method_name}()".format(
            token_type = self.formatter.get_type('token', is_relative=False),
            method_name = self.formatter.get_state_machine_method_name(section_id, is_relative=False)))
        with self.block("{", "}"):
            self.emit_state_enum()
            self.emit([
                '{token_type} token;'.format(
                    token_type = self.formatter.get_type('token', is_relative=False)),
                '{state_type} state = {initial_state};'.format(
                    state_type = self.formatter.get_type('state', is_relative=False),
                    initial_state = self.get_state_id(self.start_state)),
                'Unicode::String text;',
                'bool capture = false;'
                '',
                '// State Machine',
                'while (true)'])
            with self.block("{", "}"):
                self.line("Unicode::Codepoint c = this->peek_utf8_char();")
                self.line("switch(state)")
                with self.block("{", "}"):
                    self.emit_state_machine_cases()
                self.line("this->get_utf8_char();")
                self.line("if (capture)")
                self.line("text += c;")
            self.line()
            self.line("return Token();")

    def emit_state_enum(self):
        self.line("enum State")
        with self.block("{", "};"):
            ids = [self.get_state_id(state) for state in self.dfa]
            ids.insert(0, "INVALID_CHAR_STATE")
            for i, id in enumerate(sorted(ids)):
                if i != 0:
                    self.emitter.write(",")
                    self.emitter.close_line()
                self.emitter.open_line()
                self.emitter.write(id)
            self.emitter.close_line()
    
    def emit_state_machine_cases(self):
        self.emit_invalid_char_case()
        for i, state in enumerate(self.dfa):
            if i != 0:
                self.line()
            self.line("case {id}:".format(id=self.get_state_id(state)))
            with self.block():
                self.emit_state(state)
            
    def emit_state(self, state):
        # Capture a character if there is a possibility of completing a capture rule
        capture = False
        for rule in self.section.rules:
            if rule.id in state.ids and 'capture' in rule.action:
                self.line("capture = true;")
                break

        if len(state.edges) > 0:
            # Transition table
            state_edges = iter(state.edges.items())
            if state == self.dfa.start_state:
                with self.block("if (c == -1)"):
                    self.line("return Token(Token::{token_id});".format(token_id=self.formatter.get_token_id('endofstream')))
            elif len(state.edges) > 0:
                destination, edges = state_edges.next()
                self.emit_transition("if", destination, edges)
            for destination, edges in state_edges:
                self.emit_transition("else if", destination, edges)
            self.line("else")    
            self.emit_else_case(state, is_in_if=True)
        else:
            # Just the final action
            self.emit_else_case(state)
        self.line('break;')
        
    def emit_else_case(self, state, is_in_if=False):
        if len(state.final_ids) > 0:
            rule = self.section.get_matching_rule(state)
            if rule is None:
                raise Exception("internal error, final ID has no rule")
                
            # Section action - push or pop mode if necessary
            mode_actions = []
            action, section = rule.section_action
            if action == 'enter' or action == 'switch':
                mode_actions.append('mode.push({id});'.format(id=self.formatter.get_section_id(section)))
            if action == 'exit' or action == 'switch':
                mode_actions.insert(0, 'mode.pop();')
                if len(mode_actions) > 1:
                    mode_actions = ['{', mode_actions, '}']
                else:
                    mode_actions = [mode_actions]
                mode_actions = ['if (mode.size() > 1)'] + mode_actions
                
            # Emit final action
            if 'skip' in rule.action:
                if len(self.dfa_ir.sections) > 1:
                    block = ['return Token(Token::{id});'.format(id=self.formatter.get_token_id('skippedtoken'))]
                else:
                    block = [
                        'state = {id};'.format(id=self.get_state_id(self.start_state)),
                        'text.clear();',
                        'continue;']
            elif 'capture' in rule.action:
                block = ['return Token(Token::{id}, text);'.format(id=self.formatter.get_token_id(rule.name))]
            else:
                block = ['return Token(Token::{id});'.format(id=self.formatter.get_token_id(rule.name))]
                
            if mode_actions is not None and len(mode_actions) > 0:
                block[0:0] = mode_actions
               
            if is_in_if:
                if len(block) > 1:
                    block = ['{', block, '}']
                else:
                    block = [block]
            self.emit(block)
        else:
            # Error if there isn't a section to test
            if state == self.start_state and self.inherits:
                self.line('return {method}();'.format(method=self.formatter.get_state_machine_method_name(self.parent, is_relative=False)))
            else:
                self.line('state = {id};'.format(id=self.get_state_id('invalid_char_state')))

    def emit_transition(self, statement, destination, edges):
        cases = []
        for min_v, max_v in edges:
            if min_v == max_v:
                cases.append("c == {value}".format(value=min_v))
            else:
                cases.append("(c >= {min} && c <= {max})".format(min=min_v, max=max_v))
        with self.block("{statement} ({cases})".format(
            statement=statement, 
            cases=' || '.join(cases))):
            self.line("state = {state_id};".format(state_id=self.get_state_id(destination)))
            
        
    def emit_invalid_char_case(self):
        self.emit([
           "case {invalid_char_state_id}:".format(
                invalid_char_state_id = self.get_state_id('invalid_char_state')),
            '{', [
                'std::ostringstream oss;',
                'oss << "Invalid token: \'";',
                'for (int i=0; i < text.size(); i++)',
                '{', [
                    'if (text[i] > 31 && text[i] < 128)', [
                        'oss << (char)text[i];'],
                    'else', [
                        'oss << "\\\\x" << std::hex << std::setfill(\'0\') << std::setw(2) << text[i];']
                ], '}',
                'oss << "\'" << std::endl;',
                'this->throw_error(oss.str());'
            ], '}'])
