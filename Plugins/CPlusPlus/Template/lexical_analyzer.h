/* Copyright (C) 2014 Parker Michaels
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a 
 * copy of this software and associated documentation files (the "Software"), 
 * to deal in the Software without restriction, including without limitation 
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, 
 * and/or sell copies of the Software, and to permit persons to whom the 
 * Software is furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in 
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
 * DEALINGS IN THE SOFTWARE.
 */
 
#ifndef $HEADER_GUARD
#define $HEADER_GUARD

#include <string>
#include <iostream>
$MODE_STACK_INCLUDE
namespace $NAMESPACE
{
    namespace Unicode
    {
        typedef int Codepoint;
        typedef std::basic_string<Codepoint> String;
    }
    
    class $CLASS_NAME
    {
        public:
        struct Token
        {
            public:
            enum TokenId
            {
                $ENUM_TOKEN_IDS
            };
            
            Token();
            Token(TokenId id);
            Token(TokenId id, const Unicode::String& text);
            TokenId id;
            Unicode::String text;
        };
        $ENUM_SECTION_IDS
        $CLASS_NAME(std::istream* stream);
        $STATE_MACHINE_METHOD_DECLARATIONS
        void throw_error(std::string message);
        
        private:
        Unicode::Codepoint buffer;
        bool is_buffered;
        $MODE_STACK_DECLARATION
        int line;
        int character;
        Unicode::Codepoint get_utf8_char();
        Unicode::Codepoint peek_utf8_char();

    };
}

#endif