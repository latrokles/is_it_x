# README
#
is_it_x is a rather straightforward web app that takes a url and returns a
category for the content of the page at said url.

This was born out of a quick hack to build http://isitsafe.samuraihippo.com, an
app that determines whether a given url is "safe for work" or not. There are,
of course, a number of factors to determine this, but isitisafe looks only at
the most obvious one.

However, it's really clear that the code behind isitisafe could be used to make
similar decisions for other pages, so I broke it out in a way that would be 
easy to get it to work with a variety of things (which wasn't all that hard, as
it all depends on the training data you use and some minor settings).

The app consists of a naive Bayes classifier (adapted from chapter 6 of 
O'Reilly's "Programming Collective Intelligence") to classify text documents,
a simple crawler that downloads training data and the page the user inputs, and
a front end to make it accessible from a browser.


### more to go here about dependencies, and setup instructions
