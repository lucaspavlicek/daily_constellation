The plots shown are designed to help the user narrow down the options, while incorporating the picked constellation. Each (zenith/sky) plot will *always* contain the mystery constellation *and* the user chosen one.

The plots are a real view of the sky from some place on Earth at the current time. The plot shows the coordinates of such an observer in the upper left.

The app has a chosen "centerpoint" for each constellation. Specifically, the vertices of the Polygon object for each constellation are used. The vertices are converted to 3D vectors on a unit sphere, and the vector mean of the vertices is taken to be the constellation "center". This centerpoint gives us a way to measure exact distances between constellations and an observer's zenith.

When generating a plot that contains both a selected and mystery constellation, the app chooses an observer who would see *both* constellations' centerpoints above the horizon. In other words, the constellation centerpoints will be within 90 degrees of the middle of a given zenith plot (the observer's zenith). There is no gaurentee that the entirety of the two constellations will appear in the plot, but a good chuck should always visible. It may be ambiguous to a player whether a constellation is actually within range in some cases, and that is why the color shades are there. Consider the color shades and the counter in the constellation dropdown menu to be the final say on what counts and what doesn't. The colors also help the player keep track of their remaining possibilities.

Now, there are many possible observers that can see both the selected and msytery constellation. The app choses one such observer at random, and each feasible observer is "equally likely" (chosen isotropically), assuming I did my math right.

It is worth noting that the random seed used in this process is fixed for all players on a given day. That means if two people on the same day guess the same constellation, they will get the same plot. This is still true if they make this guess on different turns. However, this will change the next date where the same mystery constellation comes up. So each daily puzzle will play like brand new, even if the mystery constellation is repeated.

Lastly, the plots take a few seconds to load currently. This would be quite difficult to speed up any further. Please don't spam buttoms while it loads because this can crash the app and I honestly couldn't find a way to fix it.
