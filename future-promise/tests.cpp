#include "Delayed.h"
#include "Promise.h"

#include <thread>
#include <condition_variable>
#include <cassert>
#include <vector>
#include <unistd.h>
#include <iostream>


void test_get_set() {
    Promise<int> promise;
    int v = 3;
    Future<int> future = promise.res();

    std::thread thread1([&promise, v]() {
        Promise<int> p = std::move(promise);
        p.set_value(v);
    });

    assert(v == future.get());
    thread1.join();
}

void test_get_set_many() {
    Promise<int> promise;
    int v = 3;
    Future<int> future = promise.res();

    std::vector<std::thread> threads;

    std::thread thread1([&promise, v]() {
        Promise<int> p = std::move(promise);
        sleep(1);
        p.set_value(v);
    });

    for (int i = 0; i < 3; ++i) {
        threads.push_back(std::thread([future, v]() {
            Future<int> f = future;
            assert(v == f.get());
        }));
    }

    thread1.join();
    for (auto& t: threads) {
        t.join();
    }
}

void test_get_exc() {
    Promise<int> promise;
    bool flag = false;

    Future<int> future = promise.res();
    std::thread thread1([&promise]() {
        try {
            sleep(2);
            throw std::runtime_error("error");
        } catch (std::exception& e) {
            promise.set_exc();
        }
    });

    try {
        int r = future.get();
    } catch (std::exception& e) {
        flag = true;
    }

    assert(flag);
    thread1.join();
}

void test_try_get() {
    Promise<int> promise;
    int v = 12;
    std::mutex critical;
    std::condition_variable cv;

    Future<int> future = promise.res();
    bool tried = false;
    bool set = false;
    std::thread thread1([&promise, &critical, &cv, &tried, v, &set]() {
        std::unique_lock<std::mutex> lk(critical);
        cv.wait(lk, [&tried](){ return tried; });
        promise.set_value(v);
        set = true;
        cv.notify_all();
    });

    const int* r = future.try_get();
    assert(r == nullptr);

    tried = true;
    cv.notify_all();

    {
        std::unique_lock<std::mutex> lk(critical);
        cv.wait(lk, [&set](){ return set; });
        r = future.try_get();
        assert(r != nullptr);
    }

    assert(v == *r);
    thread1.join();
}

void test_try_get_exc() {
    Promise<int> promise;
    int value = 12;
    bool catched = false;
    std::mutex critical;
    std::condition_variable cv;

    Future<int> future = promise.res();
    bool tried = false;
    bool set = false;
    std::thread thread1([&promise, &critical, &cv, &tried, value, &set]() {
        std::unique_lock<std::mutex> lk(critical);
        cv.wait(lk, [&tried](){ return tried; });
        try{
            throw std::runtime_error("error");
            promise.set_value(value);
        } catch(...) {
            promise.set_exc();
        }
        set = true;
        cv.notify_all();
    });

    const int* r = future.try_get();
    assert(r == nullptr);
    tried = true;
    cv.notify_all();

    {
        std::unique_lock<std::mutex> lk(critical);
        cv.wait(lk, [&set](){ return set; });
        try {
            r = future.try_get();
        } catch(std::exception& e) {
            catched = true;
        }

    }
    assert(catched);
    thread1.join();
}

float cmp_float(float f1, float f2) {
    float d = f1 - f2;
    if (d < 0) {
        d = -d;
    }
    return d < 0.00001;
}

void test_then() {
    Promise<int> promise;
    int value = 18;
    Future<int> future = promise.res();
    std::thread thread1([&promise, value]() {
        Promise<int> p = std::move(promise);
        sleep(1);
        p.set_value(value);
    });

    Future<double> halfed = future.then<double>([](int v) { 
        return static_cast<double>(v) / 2; 
    });

    Future<double> copy = halfed;

    assert(cmp_float(static_cast<double>(value) / 2, halfed.get()));

    std::thread thread2([halfed, value]() mutable {
        assert(cmp_float(static_cast<double>(value) / 2, halfed.get()));
    });

    thread1.join();
    thread2.join();
}



void test_then_exc() {
    Promise<int> promise;
    int value = 22;
    
    Future<int> future = promise.res();

    std::thread thread1([&promise, value]() {
        Promise<int> p = std::move(promise);
        sleep(1);
        try {
            throw std::runtime_error("error");
        } catch(...) {
            p.set_exc();
        }
    });

    Future<double> halfed = future.then<double>([](int v){ return static_cast<double>(v) / 2; });
    Future<double> copy = halfed;

    bool catched1 = false;
    bool catched2 = false;

    try {
        assert(cmp_float(static_cast<double>(value) / 2, halfed.get()));
    } catch(std::exception& e) {
        catched1 = true;
    }
    assert(catched1);

    std::thread thread2([halfed, value, &catched2]() mutable {
        try {
            assert(cmp_float(static_cast<double>(value) / 2, halfed.get()));
        } catch (std::exception& e) {
            catched2 = true;
        }
        assert(catched2);
    });

    thread2.join();
    thread1.join();
}

int main(int argc, char** argv) {

    test_get_set();
    test_get_set_many();
    test_get_exc();
    test_try_get();
    test_try_get_exc();
    test_then();
    test_then_exc();

    return 0;
}