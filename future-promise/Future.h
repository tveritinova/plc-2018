#pragma once

#include <memory>

template <typename T>
class Future {
public:
    Future(const std::shared_ptr<Delayed<T>>& op): op(op) {}

    const T get() {
    	op->wait();
	    return *op->get_value();
	}

    const T* try_get() {
	    return op->get_value();
	}

    template<typename R>
    Future<R> then(std::function<R(const T&)> worker){
    	return Future<R>(std::make_shared<ThenDelayed<T,R>>(*this, worker));
    }

    std::shared_ptr<Delayed<T>> op;
};