flashcards-json
===============

Configurable learning tool for help with memorization

Displays a series of flashcards--screens with information about a
given subject. Users can view the cards one at a time, either
randomly or by entering the number of a specific card. Cards
can also be viewed in groups, based on selected topics.

If you choose to view a single card, you'll initially see
just a hint about its contents. This hint is like the "front"
of the card, designed to spur your memory. Press the forward
slash key (/) to flip the card over and see all the details
about its subject.

All `flashcards` information is defined in a JSON-formatted text file,
which must be specified on the command line:

   `$ python flashcards.py [source-file.json]`

CONFIGURATION
-------------

The JSON file that defines your deck of flashcards needs to
contain one parent dictionary with at least three child entries.
The first required entry is a simple string...

  `"name" :` *(a string value)*

...which serves as the overall name for your flashcard collection.

The second required entry is an array of child dictionaries...

  `"data" :` [ *(an array of dictionaries)* ]

...where you define various properties for each one of your cards.
You can define as many properties as you want, for as many cards as you
need, as long as each key in each dictionary is a string and each value
in each dictionary is a JSON data primitive. There's only one required
key in all of these child dictionaries--`title`. It's the string that
the system will use to identify the card.

The third and final required entry in your parent dictionary is an
array of strings...

  `"display_template" :` [ *(an array of strings)* ]

...in which each string is a line of text that will be displayed
when your card is viewed. The strings can have replacement tokens, of
the form `{card['property']}`. When the system calls the card's `display()`
method, these tokens will be replaced with the properties you defined in the
dictionary for the card.

There's also one optional entry you can make in your parent dictionary,
which you can use to make the system automatically assign a number to
each card:

  `"numbered" :` ( `true`|`false` )

If the `"numbered"` key is present, and set to `true`, the deck will have
a numerical key that can be used to access specific cards. The first
key is `1`. By default, the deck is unnumbered.

For a basic example of a flashcards configuration file, see [`planets.json`](https://github.com/wrycoder/python-projects/blob/master/flashcards/planets.json).

ADVANCED CONFIGURATION
----------------------

The same properties can sometimes be shared by multiple flashcards in a
given deck. A collection of United States presidents, for example, will
have several presidents who were Republicans and several other presidents
who were Democrats. You might want to view all of these cards at the same time.
But how? The answer is in yet another (optional) configuration element in
the JSON dictionary...

  `"topics" :` [ *(an array of dictionaries)* ]

...where you define each topic that multiple cards have in common.

Now here's where things get a little more complicated. The key in each dictionary
is a simple string to identify the topic. But the value in each dictionary is
yet another dictionary, with four required entries:

  `"character" :` *(a single character, identifying a menu option for this topic)*\
  `"prompt" :`    *(a string containing the text for the description in the menu)*\
  `"detail" :`    [ *(an array of strings containing text to be appended to
                   the output when the card is displayed. Replacement tokens
                   can be used here.)* ]\
  `"members" :`   [ *(an array of strings, containing the `title` properties of the\
                 cards that have this topic in common.)* ]\
\
For an example of an advanced flashcards configuration file, see [`colonies.json`](https://github.com/wrycoder/python-projects/blob/master/flashcards/colonies.json).
