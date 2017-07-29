package com.dorr.chopperdropper.model;

import com.dorr.chopperdropper.Index2;
import com.google.common.collect.ImmutableSet;

import java.util.Set;

public class Terrain implements Model, Model.StaticCollidable {
    private final ImmutableSet<Index2> mBlocks;

    public Terrain(ImmutableSet<Index2> blocks) {
        mBlocks = blocks;
    }

    @Override
    public boolean isCollision(Set<Index2> indices) {
        for (Index2 idx : indices) {
            if (idx.y < 0 || mBlocks.contains(idx)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void onCollision(Model model, Environment env) { }

    public Set<Index2> get() {
        return mBlocks;
    }

    public static Terrain create(Level level) {
        ImmutableSet.Builder<Index2> blocks = ImmutableSet.builder();
        int width = level.width(), height = level.height();
        for (int x = 0; x < width; ++x) {
            for (int y = 0; y < height; ++y) {
                if (level.get(x, y) == Level.Block.TERRAIN) {
                    blocks.add(new Index2(x, y));
                }
            }
        }
        return new Terrain(blocks.build());
    }
}
