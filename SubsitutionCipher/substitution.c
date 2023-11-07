#include <ctype.h>
#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, string argv[])
{
     //check only one key input
    if (argc != 2)
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }

    //check it only has 26 charactors
    if (strlen(argv[1]) != 26)
    {
            printf("Key must contain 26 charactors.\n");
            return 1;
    }

    //check it only contains alphabets
    for (int i = 0, len = strlen(argv[1]); i < len; i++)
    {
        if (!isalpha(argv[1][i]))
        {
            printf("Key must only contain alphabetic characters.\n");
            return 1;
        }
    }

    string key = argv[1];
    //check it only contains unique alphabets
    for (int i = 0, len = strlen(argv[1]); i < len; i++)
    {
        for (int j = i + 1; j < len; j++)
        {
            if (toupper(argv[1][i]) == toupper(argv[1][j]))
            {
                printf("Key must not contain repeated characters.\n");
                return 1;
            }
        }
    }

    //get plaintext
    string plaintext = get_string("plaintext: ");

    //print out ciphertext
    printf("ciphertext: ");

    char ciphertext;
    for (int i = 0, len = strlen(plaintext); i < len; i++)
    {
        if (isupper(plaintext[i]))
        {
            ciphertext = toupper(key[plaintext[i] - 'A']);
            printf("%c", ciphertext);
        }
        else if (islower(plaintext[i]))
        {
            ciphertext = tolower(key[plaintext[i] - 'a']);
            printf("%c", ciphertext);
        }
        else
        {
            printf("%c", plaintext[i]);
        }
    }
    printf("\n");
}