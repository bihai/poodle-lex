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

#include <stdio.h>

typedef enum ${NAMESPACE}_token_id_enum
{
    TOKEN_${ID_NAMESPACE}_INVALIDCHARACTER,
    TOKEN_${ID_NAMESPACE}_ENDOFSTREAM,
    $ENUM_TOKEN_IDS
} ${NAMESPACE}_token_id;

typedef struct ${NAMESPACE}_token_struct
{
    ${NAMESPACE}_token_id id;
    char* text;
} ${NAMESPACE}_token, *p_${NAMESPACE}_token;

${NAMESPACE}_token ${NAMESPACE}_get_token(FILE* stream);
void ${NAMESPACE}_free_token(${NAMESPACE}_token* token);

#endif
