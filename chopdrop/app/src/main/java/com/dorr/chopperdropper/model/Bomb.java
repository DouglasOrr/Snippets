package com.dorr.chopperdropper.model;

import com.badlogic.gdx.math.Circle;
import com.badlogic.gdx.math.Vector2;
import com.dorr.chopperdropper.SafeObserver;
import com.dorr.chopperdropper.control.HeliTouchControl;

import rx.Subscription;

/** Designed to hit a <code>Target</code>, may be attached to
 * a <code>Heli</code>. */
public class Bomb implements Model, Model.Updatable, Model.DynamicCollidable {
    private static final float COLLISION_RADIUS = 2;               // m
    private static final Vector2 HELI_OFFSET = new Vector2(0, -6.5f); // m

    private Heli mHeli;
    private Vector2 mPosition;
    private Vector2 mVelocity;
    private final Subscription mControlSubscription;

    public Bomb(Heli heli, HeliTouchControl control) {
        mHeli = heli;
        updatePositionFromHeli();

        mControlSubscription = control.control().subscribe(new SafeObserver<HeliTouchControl.Event>() {
            @Override
            public void onNext(HeliTouchControl.Event event) {
                if (event instanceof HeliTouchControl.BombReleaseEvent) {
                    if (mHeli != null) {
                        mHeli.disarm();
                    }
                    mHeli = null;
                }
            }
        });
    }

    @Override
    public Circle bounds() {
        return new Circle(mPosition.x, mPosition.y, COLLISION_RADIUS);
    }

    @Override
    public void onCollision(Model model, Environment env) {
        if (!(model instanceof AmmoPoint)) {
            if (mHeli != null) {
                mHeli.onCollision(this, env);
            }
            env.remove(this);
            mControlSubscription.unsubscribe();
        }
    }

    public Vector2 position() {
        return new Vector2(mPosition);
    }

    private void updatePositionFromHeli() {
        mPosition = mHeli.position().add(HELI_OFFSET);
        mVelocity = mHeli.velocity();
    }

    @Override
    public void update(float dt, Environment env) {
        if (mHeli != null) {
            updatePositionFromHeli();

        } else {
            Updater.updateBody(
                    mPosition, mVelocity,
                    new Vector2(Constants.GRAVITY), // must copy, updateBody mutates!
                    dt
            );
        }
    }
}
