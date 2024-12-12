============================================
Aktiia Blood Pressure Data Extractor
============================================

Extracing Aktiia blood pressure measurements, and uploading to Apple Health
===========================================================================

As we reach middle age, increases in blood pressure is a common ailment, and it
despite my best efforts to pretend I am not getting any older, it is something I
also suffer from.

My doctor told me to take regular blood pressure measurements and recommended
the Aktiia wrist monitor, which I of course bunged a couple of hundred quid on
by the time I got home.

The wristband operates (as far as I know, I am not a medical technician) 
by shining a light on the skin of the back of your wrist, and is able to measure 
changes to the size of blood vessels and volume of liquid, and match that to
blood pressure.

There is a bluetooth controlled blood pressure monitor (you know the kind the
squeezes your upper arm) that one uses once a month to calibrate the readings
from the shining light to whats actually on the arm.

And thats about it. It sits on my wrist almost all day, for almost all the days.

No complaints.

But they clearly have a business model, and it is focused on the consumer market
(I can tell because their site at the moment recommends giving a blood pressure
monitor as a Xmas gift to the OAP in your life.  Which is an *interesing* take)

Anyway, one of the things they dont want is that Apple company, with its Apple
iWatch taking all their lunch away.  And so they have seemingly taken a knee-jerk
reaction - make it hard to get the data they collect out of their eco-system.

The data is only downloadable via pdf. It will not connect to Apple Health (and
one guesses not to any Android collector either). It is pdf or nothing. 

And the pdf table does not have any lines around the cells.  (Side note - pdfs
are where data goes to die.  It is very hard to extract information from pdfs
because whereas you and I might see a table of readings, in the pdf its just
numbers on the page - knowing if a number is supposed to be a date or a blood
pressure reading is ... awkward.

Anyway, I want to get my data out. And I probably want to store it in Apple
Health as my iPhone is spying on every other part of my life, so if I am going
to be spied upon, its going to be the big bad CIA who can collect everything in
one place.

I think thats sarcasm.

So the roadmap is to firstly extract the readings from Aktiia pdfs (which it
will email from the app) and seocndly to work out how to upload to Apple Health.
Finally wrap it up a bit nocely so anyone else might want to do so.




Target the medical professionals



Intro
=====

Extracting blood pressure readings from pdfs
as the blood pressure app only outputs as pdf.

.. toctree::

   /reference
