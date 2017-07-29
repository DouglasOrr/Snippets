package com.dorr.chopperdropper.model;

import com.dorr.chopperdropper.Index2;

import java.util.Set;

/** Simple target. Explodes when hit by a bomb. */
public class Target implements Model, Model.StaticCollidable {
    public enum State { ALIVE, DEAD }
    private final Index2 mPosition;
    private State mState = State.ALIVE;

    public Target(Index2 position) {
        mPosition = position;
    }

    @Override
    public boolean isCollision(Set<Index2> indices) {
        return indices.contains(mPosition);
    }

    public State state() {
        return mState;
    }

    public Index2 position() {
        return mPosition;
    }

    @Override
    public void onCollision(Model model, Environment env) {
        if (model instanceof Bomb) {
            mState = State.DEAD;
        }
    }
}
