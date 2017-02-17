//
//
// C++ Interface for module: Log
//
// Description: 
//
//
// Author: exa
//
//

#ifndef Log_Interface
#define Log_Interface

#ifdef LOG
//#pragma warning("Logging turned on")
extern ostream & nlog; 
#else
//#pragma warning("Logging turned off")
// No logging required
// We shall then define the "nlog" class
// such that it will generate no code
struct nlog_t {
  nlog_t() {}
  nlog_t(ostream & os) {}
  operator ostream & () {return null_stream; }
  static ostream & null_stream;
};

template<class T>
nlog_t & operator <<(nlog_t &log, const T & x) {
  return log;
}

template<class T>
nlog_t & operator <<(nlog_t &log, T & x) {
  return log;
}

extern nlog_t nlog;
#endif


#ifdef ERROR
extern ostream & nerr;
#else
struct nerr_t {};

template<class T>
nerr_t & operator <<(nerr_t &log, const T & x) {
  return log;
}

template<class T>
nerr_t & operator <<(nerr_t &log, T & x) {
  return log;
}

extern nerr_t nerr;
#endif

#endif
