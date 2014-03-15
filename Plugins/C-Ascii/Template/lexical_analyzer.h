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
 
#ifndef POODLE_LEXICALANALYZER_H
#define POODLE_LEXICALANALYZER_H

#include <stdio.h>

typedef enum poodle_token_id_enum
{
    PTKN_INVALIDCHARACTER,
    PTKN_ENDOFSTREAM,
    $ENUM_TOKEN_IDS
} poodle_token_id;

typedef struct poodle_token_struct
{
    poodle_token_id id;
    char* text;
} poodle_token, *p_poodle_token;

poodle_token poodle_get_token(FILE* stream);
void poodle_free_token(poodle_token* token);

#endif
