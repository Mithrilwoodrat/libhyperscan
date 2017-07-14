# -*- coding: utf-8 -*-
import logging
import ctypes
import traceback
from ctypes import CFUNCTYPE, POINTER, Structure, c_int, c_uint, c_char_p, c_void_p, c_ulonglong

# typedef int hs_error_t;
hs_error_t = c_int

# struct hs_platform_info;
# typedef struct hs_platform_info hs_platform_info_t;
class hs_platform_info_t(Structure):
    pass

# struct hs_database;
# typedef struct hs_database hs_database_t;
class hs_database_t(Structure):
    pass

# struct hs_scratch;
# typedef struct hs_scratch hs_scratch_t;
class hs_scratch_t(Structure):
    pass

# struct hs_stream;
# typedef struct hs_stream hs_stream_t;
class hs_stream_t(Structure):
    pass

# typedef struct hs_compile_error {
#     char *message;
#     int expression;
# } hs_compile_error_t;
class hs_compile_error_t(Structure):
    _fields_ = [('message', c_char_p),
                ('expression', c_int)]


HS_FLAG_CASELESS=1
HS_FLAG_DOTALL=2
HS_FLAG_MULTILINE=4
HS_FLAG_SINGLEMATCH=8
HS_FLAG_ALLOWEMPTY=16
HS_FLAG_UTF8=32
HS_FLAG_UCP=64
HS_FLAG_PREFILTER=128
HS_FLAG_SOM_LEFTMOST=256

HS_MODE_BLOCK=1
HS_MODE_NOSTREAM=1
HS_MODE_STREAM=2
HS_MODE_VECTORED=4

HS_SUCCESS=0
HS_INVALID=(-1)
HS_NOMEM=(-2)
HS_SCAN_TERMINATED=(-3)
HS_COMPILER_ERROR=(-4)
HS_DB_VERSION_ERROR=(-5)
HS_DB_PLATFORM_ERROR=(-6)
HS_DB_MODE_ERROR=(-7)
HS_BAD_ALIGN=(-8)
HS_BAD_ALLOC=(-9)
HS_SCRATCH_IN_USE=(-10)
HS_ARCH_ERROR=(-11)


class LibHyperScan(object):
    def __init__(self, libpath="/usr/local/lib64/libhs.so"):
        self.libpath = libpath
        self.__loadLib(libpath)

    def __loadLib(self, libpath):
        self.lib = ctypes.cdll.LoadLibrary(libpath)
        self.db_p = POINTER(hs_database_t)()
        # typedef int (*match_event_handler)(unsigned int id,
        #                                unsigned long long from,
        #                                unsigned long long to,
        #                                unsigned int flags,
        #                                void *context);
        # context
        #  *      The pointer supplied by the user to the @ref hs_scan(), @ref
        #  *      hs_scan_vector() or @ref hs_scan_stream() function.
        self.MatchEventHandler = CFUNCTYPE(c_uint,
                                           c_uint,
                                           c_ulonglong,
                                           c_ulonglong,
                                           c_uint,
                                           c_void_p)
        self.match_event_handler = self.MatchEventHandler(self.eventHandler)

    HS_RETCODES = {
        0:"HS_SUCCESS",
        -1:"HS_INVALID",
        -2:"HS_NOMEM",
        -3:"HS_SCAN_TERMINATED",
        -4:"HS_COMPILER_ERROR",
        -5:"HS_DB_VERSION_ERROR",
        -6:"HS_DB_PLATFORM_ERROR",
        -7:"HS_DB_MODE_ERROR",
        -8:"HS_BAD_ALIGN",
        -9:"HS_BAD_ALLOC",
		-10:"HS_SCRATCH_IN_USE",
		-11:"HS_ARCH_ERROR"
    }

    # const char *hs_version(void);
    def version(self):
        self.lib.hs_version.restype = c_char_p
        return self.lib.hs_version()

    # Allocate a "scratch" space for use by Hyperscan.
 
    # This is required for runtime use, and one scratch space per thread, or
    # concurrent caller, is required.
    # hs_error_t HS_CDECL hs_alloc_scratch(const hs_database_t *db,
    #                                  hs_scratch_t **scratch);
    def alloc_scratch(self):
        if not self.db_p:
            raise RuntimeError("DataBase Uninitialized")
        scratch_p = POINTER(hs_scratch_t)()
        ret = self.lib.hs_alloc_scratch(self.db_p, ctypes.byref(scratch_p))
        if ret != HS_SUCCESS:
            logging.error(self.HS_RETCODES.get(ret))
            # self.lib.hs_free_database(self.db_p)
            raise RuntimeError("Error while allocating scratch!")
        return scratch_p

    def free_scratch(self, scratch_p):
        ret = self.lib.hs_free_scratch(scratch_p)
        if ret != HS_SUCCESS:
            logging.error(self.HS_RETCODES.get(ret))
            raise RuntimeError("Error while freeing scratch!")
        return True

    def free_database(self, db_p):
        if not db_p:
            logging.error("DataBase is NULL, no need to free!")
            return False
        ret = self.lib.hs_free_database(db_p)
        if ret != HS_SUCCESS:
            logging.error(self.HS_RETCODES.get(ret))
            raise RuntimeError("Error while freeing database!")
        return True

    # hs_error_t HS_CDECL hs_compile(const char *expression, unsigned int flags,
    #                            unsigned int mode,
    #                            const hs_platform_info_t *platform,
    #                            hs_database_t **db, hs_compile_error_t **error);
    # void hs_free_database(hs_database_t *db);

    # void hs_free_compile_error(hs_compile_error_t *error);

    def compile(self, pattern, flags=None, mode=None):
        if self.db_p:
            self.free_database(self.db_p)
        if not flags:
            flags = c_uint(HS_FLAG_DOTALL | HS_FLAG_ALLOWEMPTY)
        if not mode:
            mode = HS_MODE_NOSTREAM
        # self.db_p = POINTER(hs_database_t)()
        error_struct_p = POINTER(hs_compile_error_t)()
        retcode =  self.lib.hs_compile(pattern,
                                       flags,
                                       mode,
                                       None,
                                       ctypes.byref(self.db_p),
                                       ctypes.byref(error_struct_p))

        ret = self.HS_RETCODES.get(retcode)
        logging.info(ret)
        
        if retcode < 0:
            logging.error(error_struct_p.contents.message)
            self.lib.hs_free_compile_error(error_struct_p)
        
        return retcode

    # hs_error_t HS_CDECL hs_compile_multi(const char *const *expressions,
    #                                  const unsigned int *flags,
    #                                  const unsigned int *ids,
    #                                  unsigned int elements, unsigned int mode,
    #                                  const hs_platform_info_t *platform,
    #                                  hs_database_t **db,
    #                                  hs_compile_error_t **error);

    def compile_multi(self, patterns, ids=None, flags=None, mode=None):
        if self.db_p:
            self.free_database(self.db_p)
        elements = len(patterns)
        if len(patterns) == 0:
            raise RuntimeError("Empty Patterns!")
        assert [type(pattern) is str for pattern in patterns]
        #patterns = [c_char_p(POINTER(pattern)) for pattern in patterns]
        a_patterns = (c_char_p * len(patterns))()
        a_patterns[:] = patterns

        if ids:
            assert [type(_id) is int for _id in ids]
            ids = (c_uint * len(ids))(*ids)
        if not flags:
            flag = c_uint(HS_FLAG_DOTALL | HS_FLAG_ALLOWEMPTY)
            flags = (c_uint * elements)()
            for i in xrange(elements):
                flags[i] = flag
        if not mode:
            mode = HS_MODE_NOSTREAM
        
        error_struct_p = POINTER(hs_compile_error_t)()
        self.lib.hs_compile_multi.argtypes = [(c_char_p*len(patterns)),
                                              POINTER(c_uint),
                                              POINTER(c_uint),
                                              c_uint,
                                              c_uint,
                                              c_void_p,
                                              c_void_p,
                                              c_void_p]
                                              
        retcode =  self.lib.hs_compile_multi(a_patterns,
                                             flags,
                                             ids,
                                             elements,
                                             mode,
                                             None,
                                             ctypes.byref(self.db_p),
                                             ctypes.byref(error_struct_p))

        ret = self.HS_RETCODES.get(retcode)
        logging.info(ret)
        
        if retcode < 0:
            logging.error(error_struct_p.contents.message)
            self.lib.hs_free_compile_error(error_struct_p)
        
        return retcode

    # The block (non-streaming) regular expression scanner.
    # This is the function call in which the actual pattern matching takes place for block-mode pattern databases.
    # hs_error_t HS_CDECL hs_scan(const hs_database_t *db, const char *data,
    #                         unsigned int length, unsigned int flags,
    #                         hs_scratch_t *scratch, match_event_handler onEvent,
    #                         void *context);

    def scan(self, data, callback=None):
        if callback is None:
            callback = self.match_event_handler
        else:
            callback = self.MatchEventHandler(callback)
        scratch_p = self.alloc_scratch()
        ret = self.lib.hs_scan(self.db_p, data, len(data), 0, scratch_p, callback, data)

        self.free_scratch(scratch_p)
        logging.info(self.HS_RETCODES.get(ret))
        return ret

    
    def eventHandler(self, _id, _from, _to, flags, context):
        print _id
        print c_char_p(context).value[_from:_to]
        return 0

    def __del__(self):
        try:
            if self.db_p:
                self.free_database(self.db_p)
        except Exception as error:
            logging.error(error)

def main():
    lib = LibHyperScan()
    print lib.version()
    lib.compile('A*')
    lib.compile('BA*')
    lib.scan("BAAA")
    lib.compile("^ER.*")
    lib.scan("BAAA")
    lib.scan("ERROR, FUCK")
    lib.compile_multi(["ABC", "BAAA"], [123,456])
    lib.scan("BAAAAAAA")
    
if __name__ == "__main__":
    logging.basicConfig(
        format='[%(asctime)s] (%(module)s:%(funcName)s:%(lineno)s): <%(levelname)s> %(message)s', level=logging.INFO)
    main()


