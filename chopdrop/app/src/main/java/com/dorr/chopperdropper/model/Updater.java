package com.dorr.chopperdropper.model;

import com.badlogic.gdx.math.Circle;
import com.badlogic.gdx.math.Vector2;
import com.dorr.chopperdropper.Index2;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public class Updater {
    public static void updateBody(Vector2 position, Vector2 velocity, Vector2 specificForce, float dt) {
        specificForce.scl(dt);
        position.add(velocity.x * dt / 2, velocity.y * dt / 2);
        velocity.add(specificForce);
        position.add(velocity.x * dt / 2, velocity.y * dt / 2);
    }

    public static final float PHYSICS_DT = 0.01f; // s
    private float mRemainingTime = 0;
    private final World mWorld;

    public Updater(World world) {
        mWorld = world;
    }

    public void update(float dt) {
        mRemainingTime += dt;
        while (PHYSICS_DT < mRemainingTime) {
            updateTick(mWorld);
            mRemainingTime -= PHYSICS_DT;
        }
    }

    /** Runs a single physics tick */
    private static void updateTick(World world) {
        World.Env env = world.beginUpdate();

        // updates
        for (Model model : world.models) {
            if (model instanceof Model.Updatable) {
                ((Model.Updatable) model).update(PHYSICS_DT, env);
            }
        }

        // collisions
        List<Model.StaticCollidable> statics = new ArrayList<Model.StaticCollidable>();
        List<Model.DynamicCollidable> dynamics = new ArrayList<Model.DynamicCollidable>();
        for (Model model : world.models) {
            if (model instanceof Model.StaticCollidable) {
                statics.add((Model.StaticCollidable) model);
            }
            if (model instanceof Model.DynamicCollidable) {
                dynamics.add((Model.DynamicCollidable) model);
            }
        }
        for (Model.DynamicCollidable dynamic : dynamics) {
            Set<Index2> dynamicBlocks = world.grid.intersections(dynamic.bounds());
            for (Model.StaticCollidable staticCollidable : statics) {
                if (staticCollidable.isCollision(dynamicBlocks)) {
                    dynamic.onCollision(staticCollidable, env);
                    staticCollidable.onCollision(dynamic, env);
                }
            }
        }
        for (int i = 0; i < dynamics.size(); ++i) {
            Model.DynamicCollidable a = dynamics.get(i);
            Circle aBounds = a.bounds();
            for (int j = i + 1; j < dynamics.size(); ++j) {
                Model.DynamicCollidable b = dynamics.get(j);
                Circle bBounds = b.bounds();
                if (aBounds.overlaps(bBounds)) {
                    a.onCollision(b, env);
                    b.onCollision(a, env);
                }
            }
        }

        world.endUpdate(env);
    }
}
