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
 
 #include <iostream>
 #include <fstream>
 #include <stdexcept>
 #include "$BASE_FILE_NAME.h"
 
 using namespace $NAMESPACE;
 
 void debug_token($CLASS_NAME::Token& token);
 std::string to_str(Unicode::String str);
 
 int main(int argc, char* argv[])
 {
    if (argc != 2)
    {
        std::cout << "Usage: " << argv[0] << " [input_file_to_scan]" << std::endl;
        return 1;
    }
    
    std::ifstream f;
    f.open(argv[1], std::fstream::in);
    if (f.fail())
    {
        std::cerr << "Unable to open '" << argv[1] << "'" << std::endl;
        return 1;
    }
    
    try
    {
        $NAMESPACE::$CLASS_NAME lexer(&f);
        $CLASS_NAME::Token token;
        do
        {
            token = lexer.get_token();
            debug_token(token);
        } while (token.id != $CLASS_NAME::Token::ENDOFSTREAM);
    }
    catch (std::runtime_error ex)
    {
        std::cerr << "Error while retrieving token: " << ex.what() << std::endl;
    }
    f.close();
    return 0;
 }

 void debug_token($CLASS_NAME::Token& token)
 {
    std::string id_string;
    switch(token.id)
    {
        $SELECT_ID_STRING
        case $CLASS_NAME::Token::ENDOFSTREAM:
            id_string = "EndOfStream";
            break;
        default:
            id_string = "InvalidToken";
            break;
    }
    if (token.text.empty())
        std::cout << "Token(" << id_string << ")" << std::endl;
    else
        std::cout << "Token(" << id_string << ", '" << to_str(token.text) << "')" << std::endl;
 }
 
 std::string to_str(Unicode::String str)
 {
    std::string result;
    result.reserve(str.size());
    for (int i=0; i<str.size(); i++)
        result += (str[i] > 0 && str[i] < 128) ? (char)str[i] : '?';
    return result;
 }
