package com.dorr.chopperdropper.model;

import com.dorr.chopperdropper.Index2;

import java.util.Set;

public class AmmoPoint implements Model, Model.StaticCollidable {
    private final Index2 mIndex;

    public AmmoPoint(Index2 index) {
        mIndex = index;
    }

    @Override
    public boolean isCollision(Set<Index2> indices) {
        return indices.contains(mIndex);
    }

    @Override
    public void onCollision(Model model, Environment env) {
        if (model instanceof Heli) {
            ((Heli) model).rearm(env);
        }
    }

    public Index2 position() {
        return mIndex;
    }
}
