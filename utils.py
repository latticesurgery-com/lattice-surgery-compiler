from fractions import Fraction
import math


def decompose_pi_fraction(f:Fraction):
  """
  Break a fraction that has a power of two as denominator into a sequence of fractions 
  that add up to it, all of which have 1 for numerator.

  Adjusts the fraction to be in the (2,0] range
  """

  # Check that f's denominator is a power of two
  assert(f.denominator & (f.denominator - 1) == 0)

  # Adjust to the the (2*pi,0] range
  f = Fraction(f.numerator % (2*f.denominator), f.denominator)

  if f.numerator == 0: return [f]
  elif f.numerator == 1: return [f]
  else:
      p = int(math.log(f.numerator, 2))
      largest_pow_of_2 = int(pow(2, p))  
      return [Fraction(largest_pow_of_2, f.denominator)] \
        + decompose_pi_fraction(Fraction(f.numerator - largest_pow_of_2,f.denominator))
