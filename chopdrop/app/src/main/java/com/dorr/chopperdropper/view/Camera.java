package com.dorr.chopperdropper.view;

import com.badlogic.gdx.math.Matrix4;
import com.badlogic.gdx.math.Rectangle;
import com.badlogic.gdx.math.Vector2;
import com.dorr.chopperdropper.model.Grid;
import com.dorr.chopperdropper.model.Model;

public abstract class Camera {
    /** Update the internal state of the camera (called just before drawing). */
    public abstract void update(float viewportWidth, float viewportHeight);

    /** Get the world->screen transform matrix to use to render the scene. */
    public abstract Matrix4 transform();

    /** Get the bounding rectangle of visible elements in the world. */
    public abstract Rectangle worldBounds();

    public static Camera fixed(final Grid grid) {
        return new Camera() {
            float mScale = Float.NaN;
            float mBoundsX = Float.NaN, mBoundsY = Float.NaN;

            @Override
            public void update(float viewportWidth, float viewportHeight) {
                mScale = Math.min(viewportWidth / grid.worldWidth(), viewportHeight / grid.worldHeight());
                mBoundsX = viewportWidth / mScale;
                mBoundsY = viewportHeight / mScale;
            }

            @Override
            public Matrix4 transform() {
                return new Matrix4(new float[]{
                        mScale, 0, 0, 0,
                        0, mScale, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1});
            }

            @Override
            public Rectangle worldBounds() {
                return new Rectangle(0, 0, mBoundsX, mBoundsY);
            }
        };
    }

    public static Camera lookingAt(final Model.HasPosition model,
                                   final float yMin,
                                   final float minWorldWidth,
                                   final float maxHeightFraction) {
        return new Camera() {
            private float mScale = Float.NaN;
            private float mXMin = Float.NaN, mXMax = Float.NaN, mYMax = Float.NaN;

            @Override
            public void update(float viewportWidth, float viewportHeight) {
                Vector2 p = model.position();
                float h = p.y - yMin;
                mScale = Math.min(
                        viewportWidth / minWorldWidth,
                        0 < h ? (viewportHeight * maxHeightFraction / h) : Float.MAX_VALUE
                );
                float halfWidth = viewportWidth / mScale / 2;
                mXMin = p.x - halfWidth;
                mXMax = p.x + halfWidth;
                mYMax = yMin + viewportHeight / mScale;
            }

            @Override
            public Matrix4 transform() {
                float translateX = -mScale * mXMin;
                float translateY = -mScale * yMin;
                return new Matrix4(new float[]{
                        mScale, 0, 0, 0,
                        0, mScale, 0, 0,
                        0, 0, 1, 0,
                        translateX, translateY, 0, 1});
            }

            @Override
            public Rectangle worldBounds() {
                return new Rectangle(mXMin, yMin, mXMax - mXMin, mYMax - yMin);
            }
        };
    }
}
