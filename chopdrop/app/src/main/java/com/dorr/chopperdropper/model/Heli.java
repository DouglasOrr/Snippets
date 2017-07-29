package com.dorr.chopperdropper.model;

import com.badlogic.gdx.math.Circle;
import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.math.Vector2;
import com.dorr.chopperdropper.SafeObserver;
import com.dorr.chopperdropper.control.HeliTouchControl;

/** A helicopter, controlled by very simple physics. */
public class Heli implements Model, Model.HasPosition, Model.Updatable, Model.DynamicCollidable {
    private static final float MASS = 80;              // kg
    private static final float MAX_ROTOR_FORCE = 3000; // N
    private static final float REVERSE_LIMIT = 0.7f;   // fraction of MAX_ROTOR_FORCE
    private static final float MAX_ANGLE_CHANGE = 2;   // rad/s
    private static final float COLLISION_RADIUS = 4;   // m

    private final HeliTouchControl mControl;

    private Vector2 mPosition = new Vector2(); // m
    private Vector2 mVelocity = new Vector2(); // m
    private float mAngle = 0; // rad (anticlockwise from vertical)
    private float mPowerControl = 0, mAngleControl = 0;

    public enum State { START, FLYING, CRASHED }
    private State mState = State.START;
    private boolean mArmed = false;

    public Heli(Vector2 position, HeliTouchControl control) {
        mPosition = position;
        mControl = control;
        control.control().subscribe(new SafeObserver<HeliTouchControl.Event>() {
            @Override
            public void onNext(HeliTouchControl.Event event) {
                if (event instanceof HeliTouchControl.ControlEvent) {
                    HeliTouchControl.ControlEvent c = (HeliTouchControl.ControlEvent) event;
                    if (mState == State.START) {
                        mState = State.FLYING;
                    }
                    mPowerControl = MathUtils.clamp(c.power, -REVERSE_LIMIT, 1);
                    mAngleControl = MathUtils.clamp(c.rotation, -1, 1);
                }
            }
        });
    }

    private Vector2 up() {
        return new Vector2(0, 1).rotateRad(mAngle);
    }

    public Vector2 position() {
        return new Vector2(mPosition);
    }
    public Vector2 velocity() {
        return new Vector2(mVelocity);
    }

    public float angle() {
        return mAngle;
    }

    public State state() {
        return mState;
    }

    public void rearm(Environment env) {
        if (!mArmed && mState != State.CRASHED) {
            mArmed = true;
            env.add(new Bomb(this, mControl));
        }
    }
    public void disarm() {
        mArmed = false;
    }

    @Override
    public void onCollision(Model that, Environment env) {
        if (!(that instanceof AmmoPoint)) {
            mState = State.CRASHED;
            mArmed = false;
        }
    }

    @Override
    public Circle bounds() {
        return new Circle(mPosition.x, mPosition.y, COLLISION_RADIUS);
    }

    @Override
    public void update(float dt, Environment env) {
        if (mState == State.FLYING) {
            mAngle += MAX_ANGLE_CHANGE * mAngleControl * dt;
            float rotorForce = MAX_ROTOR_FORCE * mPowerControl;
            Updater.updateBody(
                    mPosition, mVelocity,
                    new Vector2()
                        .add(Constants.GRAVITY)
                        .add(up().scl(rotorForce / MASS)),
                    dt
            );
        }
    }
}
