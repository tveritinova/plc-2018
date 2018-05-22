#pragma once

#include <memory>
#include <condition_variable>
#include <mutex>
#include <functional>

template<typename T>
class Delayed;
template<typename T, typename R>
class ThenDelayed;

#include "Future.h"

template<typename T>
class Delayed {
public:

    Delayed(): exception(nullptr), terminated(false) {}

    virtual void wait() {
        std::unique_lock<std::mutex> lock(critical);
        cv.wait(lock, [this]() {
            if (value.get() == nullptr && exception == nullptr && terminated) {
                throw std::runtime_error("invalid");
            }
            return value.get() != nullptr || exception != nullptr;
        });
    }

    virtual T* get_value() {
        std::lock_guard<std::mutex> guard(critical);
        if (exception != nullptr) {
            std::rethrow_exception(exception);
        }
        return value.get();
    }

    void set_value(const T& v) {
        std::lock_guard<std::mutex> lock(critical);
        if (value != nullptr || exception != nullptr) {
            throw std::runtime_error("value already set");
        }
        value = std::move(std::make_unique<T>(v));
        cv.notify_all();
    }

    void set_exc() {
        std::lock_guard<std::mutex> lock(critical);
        if (value != nullptr || exception != nullptr) {
            throw std::runtime_error("value already set");
        }
        exception = std::current_exception();
        cv.notify_all();
    }

    void try_throw() const {
        std::lock_guard<std::mutex> guard(critical);
        if (exception != nullptr) {
            std::rethrow_exception(exception);
        }
    }

    void terminate() {
        std::lock_guard<std::mutex> lock(critical);
        terminated = true;
        cv.notify_all();
    }

    std::unique_ptr<T> value;
    std::exception_ptr exception;

    std::mutex critical;
    std::condition_variable cv;

    bool terminated;
};


template<typename T, typename R>
class ThenDelayed: public Delayed<R> {
public:

    ThenDelayed(Future<T> future, std::function<R(const T&)> worker):
        future(future),
        worker(worker) {}

    virtual void wait() override { return; }

    virtual R* get_value() override {

        std::lock_guard<std::mutex> guard(this->critical);

        if (this->exception != nullptr) {
            std::rethrow_exception(this->exception);
        }
        if (this->value != nullptr) {
            return this->value.get();
        }

        this->value = std::move(std::make_unique<R>(worker(future.get())));
        this->cv.notify_all();
        return this->value.get();
    }

    Future<T> future;
    std::function<R(const T&)> worker;
};