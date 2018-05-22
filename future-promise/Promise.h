#pragma once

#include <memory>

#include "Delayed.h"

template <typename T>
class Promise {
public:

    Promise(): op(new Delayed<T>()) {}

    ~Promise() { 
        op->terminate(); 
    }

    void set_value(const T& value) { 
        op->set_value(value); 
    }

    void set_exc() { 
        op->set_exc(); 
    }

    Future<T> res() { 
        return Future<T>(op); 
    }

    std::shared_ptr<Delayed<T>> op;
};