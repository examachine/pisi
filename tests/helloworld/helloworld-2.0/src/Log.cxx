//
//
// C++ Implementation for module: Log
//
// Description: 
//
//
// Author: exa
//
//

#include <iostream>
#include "Log.hxx"


#ifdef LOG

ostream & nlog = cerr;

#else

nlog_t nlog;

ostream & nlog_t::null_stream = cerr;

#endif

#ifdef ERROR

ostream & nerr = cerr;

#else

nerr_t nerr;

#endif
