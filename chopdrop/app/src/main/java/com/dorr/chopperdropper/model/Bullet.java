package com.dorr.chopperdropper.model;

import com.badlogic.gdx.math.Circle;
import com.badlogic.gdx.math.Vector2;

/** Contains a single bullet that is in flight. */
public class Bullet implements Model, Model.HasPosition, Model.Updatable, Model.DynamicCollidable {
    private static final float LIFETIME = 1; // s
    private final Vector2 mPosition;
    private final Vector2 mVelocity;
    private float mLife = LIFETIME;

    public Bullet(Vector2 position, Vector2 velocity) {
        mPosition = position;
        mVelocity = velocity;
    }

    @Override
    public Vector2 position() {
        return mPosition.cpy();
    }

    @Override
    public Circle bounds() {
        return new Circle(mPosition, 0);
    }

    @Override
    public void onCollision(Model model, Environment env) {
        env.remove(this);
    }

    @Override
    public void update(float dt, Environment env) {
        mPosition.add(mVelocity.x * dt, mVelocity.y * dt);
        mLife -= dt;
        if (mLife < 0) {
            env.remove(this);
        }
    }
}
