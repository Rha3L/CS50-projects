#include <cs50.h>
#include <stdio.h>

long get_num(void);
int check_length(long card);

int main(void)
{
    //Ask for CC number
    long card = get_num();

    //Check CC length
    int length = check_length(card);

    if ((length != 13) && (length != 15) && (length != 16))
    {
        printf("INVALID\n");
    }

    //Store card number in array
    int number[length];
    for (int i = 0; i < length; i++)
    {
        number[i] = card % 10;
        card = card / 10;
    }

    int card_array[length];
    for (int i = 1; i < length; i++)
    {
        card_array[i] = number[i];
    }

    //Store every other digit (starting with second to last) and multiply by 2
    for (int i = 1; i < length; i+=2)
    {
        number[i] = number[i] * 2;
    }

    //Check if it's VISA, AMEX or MASTERCARD
    int n = 0;
    int temp;

    if (length == 13)
    {
      for (int i = 0; i < length; i++)
      {
        temp = (number[i] % 10) + (number[i]/10 % 10);
        n = n + temp;
      }
      if (card_array[12] == 4 && n % 10 == 0)
      {
        printf("VISA\n");
      }
      else
      {
        printf("INVALID\n");
      }
    }
    if (length == 15)
    {
      for (int i = 0; i < length; i++)
      {
        temp = (number[i] % 10) + (number[i]/10 % 10);
        n = n + temp;
      }
      if (card_array[14] == 3 && n % 10 == 0 && (card_array[13] == 4 || card_array[13] == 7))
      {
        printf("AMEX\n");
      }
      else
      {
        printf("INVALID\n");
      }
    }
    if (length == 16)
    {
      for (int i = 0; i < length; i++)
      {
        temp = (number[i] % 10) + (number[i]/10 % 10);
        n = n + temp;
      }
      if (card_array[15] == 4 && n % 10 == 0)
      {
        printf("VISA\n");
      }
      else if (card_array[15] == 5 && n % 10 == 0 && (card_array[14] == 1 || card_array[14] == 2 || card_array[14] == 3 || card_array[14] == 4 || card_array[14] == 5))
        {
            printf("MASTERCARD\n");
        }
      else
      {
        printf("INVALID\n");
      }
    }

    return 0;
}

long get_num(void)
{
    long n;
    do
    {
        n = get_long("Number: ");
    }
    while (n < 0);
    return n;
}

int check_length(long card)
{
  int n = 0;
  while (card > 0)
    {
        card = card /10;
        n++;
    }
  return n;
}