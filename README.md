# Kalkulikus & Gumoś

> *One step back. One more step back.  
> Okay, I'm out of the box now. What can I see from here?*

It started with a very simple question:

**Do I really need the decimal system to rebase a number from HEX to DOZ?**

Almost every conventional solution I found followed the same path:

    HEX → DEC → DOZ

It works. But why should decimal be special?

## The idea

Instead of asking *"how do I calculate the value in another numeral system?"*,
I started looking at numeral systems as different scales describing the same
position.

That led to **Gumoś** — a "rubber" numeric axis.

The number does not need to move. The scale can stretch.

From there the idea evolved into **Kalkulikus**: an experimental mechanical
calculating model built from stretchable rings, gears, counters and levers.

A numeral system is essentially its ordered set of symbols:

    BIN = 01
    OCT = 01234567
    DEC = 0123456789
    DOZ = 0123456789AB
    HEX = 0123456789ABCDEF

The machine operates on those symbols and their positions rather than treating
decimal representation as the universal intermediate language.

## What's inside?

**Gumoś** explores the original rubber-scale idea and uses it for operations
such as multiplication and division.

**Kalkulikus** takes the idea further and models a calculating machine using:

- stretchable symbol rings
- interconnected gears
- gear-based counters (`Klicznik`)
- state levers
- arithmetic and relational operations
- rebasing between numeral systems

The point of the project is not to replace Python's arithmetic or provide the
fastest base converter ever written.

It is an experiment in changing the abstraction.

Sometimes the interesting solution appears only after stepping far enough
away from the original problem.
