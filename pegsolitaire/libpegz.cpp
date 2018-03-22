#include "Python.h"
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "arrayobject.h"
#include <algorithm>

namespace {
    PyObject* get_symmetric_identifier(PyObject*, PyObject* args) {
        PyObject* py_pegs;
        if (!PyArg_ParseTuple(args, "O", &py_pegs)) {
            return nullptr;
        }
        PyArrayObject* np_pegs = reinterpret_cast<PyArrayObject*>(PyArray_FROM_OTF(py_pegs, NPY_BOOL, NPY_ARRAY_IN_ARRAY));
        const char* pegs = PyArray_BYTES(np_pegs);
        auto sum_off = 0ull, sum_ofr = 0ull, sum_orf = 0ull, sum_orr = 0ull;
        auto sum_tff = 0ull, sum_tfr = 0ull, sum_trf = 0ull, sum_trr = 0ull;
        auto level = 1ull;
        const auto n = PyArray_DIMS(np_pegs)[0];
        for (auto idx = 0; idx < n*n; ++idx, level <<= 1) {
            auto x = idx % n;
            auto y = idx / n;
            sum_off += pegs[n*y + x] * level;
            sum_ofr += pegs[n*y + n-1-x] * level;
            sum_orf += pegs[n*(n-1-y) + x] * level;
            sum_orr += pegs[n*(n-1-y) + n-1-x] * level;
            sum_tff += pegs[n*x + y] * level;
            sum_tfr += pegs[n*x + n-1-y] * level;
            sum_trf += pegs[n*(n-1-x) + y] * level;
            sum_trr += pegs[n*(n-1-x) + n-1-y] * level;
        }
        auto sum = std::min(std::min(std::min(sum_off, sum_ofr), std::min(sum_orf, sum_orr)),
                            std::min(std::min(sum_tff, sum_tfr), std::min(sum_trf, sum_trr)));
        Py_DECREF(np_pegs);
        return Py_BuildValue("K", sum);
    }

    void create_move(PyArrayObject* src, int n, int y, int x, int dy, int dx,
                          PyObject* result) {
        PyArrayObject* a = reinterpret_cast<PyArrayObject*>(PyArray_NewCopy(src, NPY_ANYORDER));
        char* data = PyArray_BYTES(a);
        data[n*y + x] = 0;
        data[n*(y+dy) + (x+dx)] = 0;
        data[n*(y+2*dy) + (x+2*dx)] = 1;
        PyList_Append(result, reinterpret_cast<PyObject*>(a));
        Py_DECREF(a);
    }

    PyObject* get_moves(PyObject*, PyObject* args) {
        PyObject* py_mask;
        PyObject* py_pegs;
        if (!PyArg_ParseTuple(args, "OO", &py_mask, &py_pegs)) {
            return nullptr;
        }
        PyArrayObject* np_mask = reinterpret_cast<PyArrayObject*>(PyArray_FROM_OTF(py_mask, NPY_BOOL, NPY_ARRAY_IN_ARRAY));
        PyArrayObject* np_pegs = reinterpret_cast<PyArrayObject*>(PyArray_FROM_OTF(py_pegs, NPY_BOOL, NPY_ARRAY_IN_ARRAY));
        const char* mask = PyArray_BYTES(np_mask);
        const char* pegs = PyArray_BYTES(np_pegs);
        const auto n = PyArray_DIMS(np_pegs)[0];
        PyObject* result = PyList_New(0);
        for (auto idx = 0; idx < n*n; ++idx) {
            auto x = idx % n;
            auto y = idx / n;
            if (pegs[n*y + x]) {
                if (x+2 < n && mask[n*y + x+2] && pegs[n*y + x+1] && !pegs[n*y + x+2]) {
                    create_move(np_pegs, n, y, x, 0, 1, result);
                }
                if (0 <= x-2 && mask[n*y + x-2] && pegs[n*y + x-1] && !pegs[n*y + x-2]) {
                    create_move(np_pegs, n, y, x, 0, -1, result);
                }
                if (y+2 < n && mask[n*(y+2) + x] && pegs[n*(y+1) + x] && !pegs[n*(y+2) + x]) {
                    create_move(np_pegs, n, y, x, 1, 0, result);
                }
                if (0 <= y-2 && mask[n*(y-2) + x] && pegs[n*(y-1) + x] && !pegs[n*(y-2) + x]) {
                    create_move(np_pegs, n, y, x, -1, 0, result);
                }
            }
        }
        Py_DECREF(np_mask);
        Py_DECREF(np_pegs);
        return result;
    }

    PyMethodDef methods[] = {
        { "get_symmetric_identifier", get_symmetric_identifier, METH_VARARGS,
          "Get a symmetric ID for an array of pegs" },
        { "get_moves", get_moves, METH_VARARGS,
          "Get a list of valid moves" },
        { nullptr, nullptr, 0, nullptr }
    };

    struct PyModuleDef module = {
        PyModuleDef_HEAD_INIT,
        "pegz",
        "Extention library for peg solitaire in numpy",
        -1,
        methods,
        nullptr,
        nullptr,
        nullptr,
        nullptr
    };

} // namespace (anonymous)

PyMODINIT_FUNC PyInit_libpegz() {
    import_array();
    return PyModule_Create(&module);
}
