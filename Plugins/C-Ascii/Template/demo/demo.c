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
 #include "$BASE_FILE_NAME.h"
 
 int main(int argc, char* argv[])
 {
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s [input_file_to_scan]\n", argv[0]);
        exit(1);
    }
    
    FILE* f = fopen(argv[1], "r");
    if (f == NULL)
    {
        fprintf(stderr, "Unable to open '%s'\n", argv[1]);
        exit(1);
    }
    
    ${NAMESPACE}_token token;
    int done = 0;
    while (!done)
    {
        token = ${NAMESPACE}_get_token(f);
        ${NAMESPACE}_debug_token(&token, stdout);
        printf("\n");
        if (token.id == TOKEN_${ID_NAMESPACE}_ENDOFSTREAM)
            done = 1;
        ${NAMESPACE}_free_token(&token);
    }
    fclose(f);
 }
