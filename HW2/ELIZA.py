import sys
import itertools
import operator
import re

def regexHandler(userInput):
    original_copy = userInput
    responseStr = "Please go on."
    
    userInput = re.sub(r'\b(yes)\b','I see', userInput)
    
    userInput = re.sub(r'\b(no)\b', 'Why not?', userInput)
    
    userInput = re.sub(r'\b(goodbye)\b','Goodbye!', userInput)

    userInput = re.sub(r'(.*\byou\b.*)', 'Let\'s not talk about me.', userInput)

    userInput = re.sub(r'what is (.*)', 'Why do you ask about \\1', userInput)

    userInput = re.sub(r'(.*) i am (.*)', 'Do you enjoy being \\2', userInput)
    
    userInput = re.sub(r'why is (.*)', 'Why do you think \\1', userInput)

    userInput = re.sub(r'my (.*)', 'Your \\1', userInput)

    # Newly added
    userInput = re.sub(r'this is (.*)', 'That is \\1', userInput)

    userInput = re.sub(r'(he|she|his|her|we) (.*)','\\1 \\2?', userInput)

    userInput = re.sub(r'do i (.*)', 'I could not tell if you \\1.', userInput)

    userInput = re.sub(r'what do people (.*) for (.*)', 'I don\'t know what people \\1 for \\2', userInput)
    

    userInput = responseStr if userInput == original_copy else userInput
    return userInput

def main():

    userIn = input('> ')
    while(True):
        response = regexHandler(userIn.lower())
        print('ELIZA: ' + response)
        if(response == 'Goodbye!'):
            break
        userIn = input('> ')

    print('ELIZA EXITED')


if __name__ == '__main__':
    main()