#pragma once
#include <sstream>
#include <ostream>
#include <cassert>

namespace LittleLanguage {

    template<class T>
    struct Option {
        // Failing option
        Option() : m_value(0) { }
        // Succeeding option (unless value = 0)
        explicit Option(T* value) : m_value(value) { }
        // Deep copy
        Option(const Option<T>& opt)
            : m_value(opt.exists() ? new T(*opt) : 0) {
            m_error.str(opt.m_error.str());
        }
        ~Option() { if (exists()) { delete m_value; } }
        // Deep assign
        Option<T>& operator=(const Option<T>& opt) {
            if (&opt != this) {
                if (exists()) { delete m_value; }
                m_value = opt.exists() ? new T(*opt) : 0;
                m_error.str(opt.m_error.str());
            }
            return *this;
        }

        bool exists() const { return m_value != 0; }
        bool operator!() const { return !exists(); }

        std::ostream& err() { assert(!exists()); return m_error; }
        std::string errorMessage() const { assert(!exists()); return m_error.str(); }

        T& operator*() const { assert(exists()); return *m_value; }
        T* operator->() const { assert(exists()); return m_value; }

    private:
        T* m_value;
        std::ostringstream m_error;
    };

    template<class T>
    std::ostream& operator<<(std::ostream& out, const Option<T>& opt) {
        if (opt.exists()) return out << "Success: " << *opt;
        else              return out << "Failure: " << opt.errorMessage();
    }

} // namespace LittleLanguage
