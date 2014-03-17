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
 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lexical_analyzer.h"
#define MAX_TOKEN_LENGTH 4096

typedef enum poodle_state_enum
{
    $ENUM_STATE_IDS
} poodle_state;

static char* token_strings[] = {
    "InvalidCharacter",
    "EndOfStream",
    $TOKEN_IDNAMES
};

int capture(poodle_token_id id)
{
    switch(id)
    {
        case PTKN_INVALIDCHARACTER:
        $CAPTURE_CASES
            return 1;
        default:
            return 0;
    }
}

void poodle_debug_token(poodle_token* token, FILE* f)
{
    if (!f)
        return;
    else if (!token)
        fprintf(f, "(Null)");
    else if (token->id < 0 || token->id >= PTKN_TOKENIDCOUNT)
        fprintf(f, "(Invalid ID)");
    else if (token->text == NULL)
        fprintf(f, "Token(%s)", token_strings[token->id]);
    else
        fprintf(f, "Token(%s, '%s')", token_strings[token->id], token->text);
}

void poodle_free_token(poodle_token* token)
{
    if (!token)
        return;
    if (token->text != NULL)
    {
        free(token->text);
        token->text = NULL;
    }
}

poodle_token poodle_get_token(FILE* f)
{
    poodle_token token;
    poodle_state state = $INITIAL_STATE;
    char token_buffer[MAX_TOKEN_LENGTH], c;
    int token_index = 0;
    int done = 0;
    
    // State machine
    while (!done)
    {
        token_buffer[token_index] = c = fgetc(f);
        if (token_index == MAX_TOKEN_LENGTH-1)
            token_buffer[token_index] = c = EOF;
        token_index++;
        
        switch(state)
        {
            case $INVALID_CHAR_STATE:
                token.id = PTKN_INVALIDCHARACTER;
                done = 1;
                break;
            $STATE_MACHINE
        }
    }
    
    // Emit token
    if (capture(token.id) && token_index > 0)
    {
        token.text = malloc(token_index);
        if (token.text > 0)
        {
            strncpy(token.text, token_buffer, token_index-1);
            token.text[token_index-1] = 0;
        }
    }
    else
        token.text = NULL;
    ungetc(c, f);
    return token;
}
