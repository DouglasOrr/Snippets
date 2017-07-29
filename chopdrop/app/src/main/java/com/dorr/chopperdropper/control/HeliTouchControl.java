package com.dorr.chopperdropper.control;

import com.badlogic.gdx.InputProcessor;
import com.google.common.base.Objects;

import rx.Observable;
import rx.subjects.PublishSubject;

/**
 * A simple touch-drag based controller for a Heli.
 * <p>The initial touch down location is used as a reference point, all control actions
 * are relative to that. Vertical drag (+x) is used to control rotor power. Horizontal
 * drag (-y) is used to control direction change. On touch up, the power is 'remembered',
 * it is unchanged, but the direction change is set to zero (so the helicopter stops
 * rotating when you lift your finger).</p>
 */
public class HeliTouchControl implements InputProcessor {
    private static final float SENSITIVITY = 100; // pixels

    public static abstract class Event { }

    public static final class ControlEvent extends Event {
        public final float power;
        public final float rotation;

        public ControlEvent(float power, float rotation) {
            this.power = power;
            this.rotation = rotation;
        }

        @Override
        public boolean equals(Object o) {
            if (o == null || this.getClass() != o.getClass()) {
                return false;
            }
            ControlEvent that = (ControlEvent) o;
            return this.power == that.power
                    && this.rotation == that.rotation;
        }

        @Override
        public int hashCode() {
            return Objects.hashCode(power, rotation);
        }

        @Override
        public String toString() {
            return Objects.toStringHelper(this)
                    .add("power", power)
                    .add("rotation", rotation)
                    .toString();
        }
    }

    public static final class BombReleaseEvent extends Event {
        @Override
        public boolean equals(Object that) {
            return that instanceof BombReleaseEvent;
        }
        @Override
        public int hashCode() {
            return getClass().hashCode();
        }
        @Override
        public String toString() {
            return Objects.toStringHelper(this).toString();
        }
    }

    private int mXDown = 0, mYDown = 0;
    private float mPower = 0;
    private PublishSubject<Event> mControl = PublishSubject.create();

    public Observable<Event> control() {
        return mControl;
    }

    @Override
    public boolean touchDown(int screenX, int screenY, int pointer, int button) {
        if (pointer == 0) {
            mXDown = screenX;
            mYDown = screenY;
        }
        if (pointer == 1) {
            mControl.onNext(new BombReleaseEvent());
        }
        return false;
    }

    @Override
    public boolean touchDragged(int screenX, int screenY, int pointer) {
        if (pointer == 0) {
            int dx = screenX - mXDown;
            int dy = screenY - mYDown;
            mPower = -dy / SENSITIVITY;
            mControl.onNext(new ControlEvent(mPower, -dx / SENSITIVITY));
        }
        return false;
    }

    @Override
    public boolean touchUp(int screenX, int screenY, int pointer, int button) {
        if (pointer == 0) {
            // keep power the same, but stop any additional rotation
            mControl.onNext(new ControlEvent(mPower, 0));
        }
        return false;
    }

    // *** ignored ***

    @Override
    public boolean keyDown(int keycode) {
        return false;
    }
    @Override
    public boolean keyUp(int keycode) {
        return false;
    }
    @Override
    public boolean keyTyped(char character) {
        return false;
    }
    @Override
    public boolean mouseMoved(int screenX, int screenY) {
        return false;
    }
    @Override
    public boolean scrolled(int amount) {
        return false;
    }
}
