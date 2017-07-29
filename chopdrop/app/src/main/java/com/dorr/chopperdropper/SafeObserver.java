package com.dorr.chopperdropper;

import rx.Observer;
import rx.exceptions.OnErrorFailedException;

public abstract class SafeObserver<T> implements Observer<T> {
    @Override
    public void onCompleted() { }

    @Override
    public void onError(Throwable e) {
        throw new OnErrorFailedException(e);
    }
}
