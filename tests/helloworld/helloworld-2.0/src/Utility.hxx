//
//
// C++ Interface for module: Utility
//
// Description: 
//
//
// Author: exa
//
//

#ifndef Utility_Interface
#define Utility_Interface

#include "General.hxx"

namespace Utility {

  class CPU_Time {
  public:
    CPU_Time() : clock_rep( clock() ) {} // current time
    CPU_Time(clock_t c) : clock_rep(c) {}
    //Time(time_t t) : time_rep(t) {}
    //operator const time_t() { return time_rep; }
    CPU_Time operator -(const CPU_Time rhs) {
      return CPU_Time(clock_rep - rhs.clock_rep);
    }
    ostream& print(ostream& out = cout) {
      out << double(clock_rep)/CLOCKS_PER_SEC << " seconds";
      return out;
    }
  private:
    clock_t clock_rep;
  };

  inline ostream& operator <<(ostream& out, CPU_Time t) {
    return t.print(out);
  }

  // simple counter class
  class Counter {
  public:
    Counter(int val): value(val) {}
    int operator()() { return value++; }
    int check() { return value; }
  private:
    int value;
  };

  // wrapper for rand functions
  class Rand {
  public:
    static void init() {
      seed += time(0);
      srand(seed);
      srand(rand());
    }
    static double rand_double (double upper_bound) {
      return double(rand()) * upper_bound / RAND_MAX; 
    }

    static int rand_int (int upper_bound) {
      return rand() % upper_bound; 
    }
  private:
    static int seed;
  };
 
} // namespace


#endif
