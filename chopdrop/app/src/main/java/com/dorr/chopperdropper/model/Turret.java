package com.dorr.chopperdropper.model;

import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.math.Vector2;
import com.dorr.chopperdropper.Index2;

/**
 * Aims & fires at the same target constantly (probably the Heli).
 */
public class Turret implements Model, Model.Updatable {
    private static final float FIRE_DELAY = 1; // s
    private static final float BULLET_VELOCITY = 100; // m/s

    private final Index2 mIndex;
    private final Vector2 mPosition;
    private final HasPosition mTarget;

    private float mAngle = 0; // rad (anticlockwise from vertical)
    private float mFireRecharge = 0;

    public Turret(Index2 index, Grid grid, HasPosition target) {
        mIndex = index;
        mPosition = grid.center(index);
        mTarget = target;
    }

    public float angle() { return mAngle; }

    public Index2 index() { return mIndex; }

    @Override
    public void update(float dt, Environment env) {
        Vector2 delta = new Vector2(mTarget.position()).sub(mPosition);
        mAngle = MathUtils.clamp((float) Math.atan2(-delta.x, delta.y), -MathUtils.PI / 2, MathUtils.PI / 2);

        mFireRecharge += dt;
        if (FIRE_DELAY < mFireRecharge) {
            Vector2 up = new Vector2(0, 1).rotateRad(mAngle);
            Vector2 start = mPosition.cpy().add(up.x * Grid.BLOCK_SIZE / 2, up.y * Grid.BLOCK_SIZE / 2);
            Vector2 velocity = new Vector2(up.x * BULLET_VELOCITY, up.y * BULLET_VELOCITY);
            env.add(new Bullet(start, velocity));
            mFireRecharge -= FIRE_DELAY;
        }
    }
}
