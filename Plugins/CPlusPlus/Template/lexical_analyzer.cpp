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
 
#include <string>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include "$BASE_FILE_NAME.h"

using namespace $NAMESPACE;

$CLASS_NAME::$CLASS_NAME(std::istream* stream)
{
    this->line = 1;
    this->character = 1;
    this->is_buffered = false;
    this->stream = stream;
}

Unicode::Codepoint $CLASS_NAME::peek_utf8_char()
{
    if (this->is_buffered)
        return this->buffer;
    this->buffer = this->get_utf8_char();
    this->is_buffered = true;
    return this->buffer;
}

Unicode::Codepoint $CLASS_NAME::get_utf8_char()
{
    if (this->is_buffered)
    {
        this->is_buffered = false;
        return this->buffer;
    }

    unsigned char c0, c1, c2, c3;
    this->stream->read((char*)&c0, 1);
    if (c0 == '\n')
    {
        this->line++;
        this->character = 1;
    }
    else
        this->character++;
        
    if (this->stream->eof())
        return -1;
    if (c0 < 128)
        return (Unicode::Codepoint) c0;
    else if ((c0 & 0b11100000) == 0b11000000)
    {
        this->stream->read((char*)&c1, 1);
        return 
            ((Unicode::Codepoint)(c0 & 0b00011111) << 6) | 
            (Unicode::Codepoint)(c1 & 0b00111111); 
    }
    else if ((c0 & 0b11110000) == 0b11100000)
    {
        this->stream->read((char*)&c1, 1);
        this->stream->read((char*)&c2, 1);
        return 
            ((Unicode::Codepoint)(c0 & 0b00001111) << 12) |
            ((Unicode::Codepoint)(c1 & 0b00111111) << 6) |
            (Unicode::Codepoint)(c2 & 0b00111111);
    }
    else if ((c0 & 0b11111000) == 0b11110000)
    {
        this->stream->read((char*)&c1, 1);
        this->stream->read((char*)&c2, 1);
        this->stream->read((char*)&c3, 1);
        return 
            ((Unicode::Codepoint)(c0 && 0b00000111) << 18) |
            ((Unicode::Codepoint)(c1 && 0b00111111) << 12) |
            ((Unicode::Codepoint)(c2 && 0b00111111) << 6) |
            (Unicode::Codepoint)(c3 && 0b00111111);
    }
    else
        this->throw_error("Invalid unicode character");
}

void $CLASS_NAME::throw_error(std::string message)
{
    std::ostringstream oss;
    oss << "Line " << this->line << ", character " << this->character << ": " << message;
    throw std::runtime_error(oss.str());
}

namespace $NAMESPACE
{
    enum State
    {
        $ENUM_STATE_IDS
    };
}

$CLASS_NAME::Token $CLASS_NAME::get_token()
{
    $CLASS_NAME::Token token;
    State state = $INITIAL_STATE;
    Unicode::String text;
    bool capture = false;
   
    // State machine
    while (true)
    {
        Unicode::Codepoint c = this->peek_utf8_char();
        switch(state)
        {
            case $INVALID_CHAR_STATE:
            {
                std::ostringstream oss;
                oss << "Invalid token: '";
                for (int i=0; i < text.size(); i++)
                {
                    if (text[i] > 31 && text[i] < 128)
                        oss << (char)text[i];
                    else
                        oss << "\\x" << std::hex << std::setfill('0') << std::setw(2) << text[i];
                }
                oss << "'" << std::endl;
                this->throw_error(oss.str());
            }    
            $STATE_MACHINE
        }
        
        this->get_utf8_char();
        if (capture)
            text += c;
    }
    
    return $CLASS_NAME::Token();
}

$CLASS_NAME::Token::Token()
    : id(INVALIDCHARACTER)
{ }

$CLASS_NAME::Token::Token($CLASS_NAME::Token::TokenId id) 
    : id(id)
{ }

$CLASS_NAME::Token::Token($CLASS_NAME::Token::TokenId id, const Unicode::String& text)
    : id(id), text(text)
{ }