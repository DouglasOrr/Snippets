package com.dorr.chopperdropper.view;

import com.badlogic.gdx.math.Matrix4;
import com.badlogic.gdx.math.Rectangle;
import com.badlogic.gdx.math.Vector2;
import com.badlogic.gdx.math.Vector3;
import com.dorr.chopperdropper.model.Grid;
import com.dorr.chopperdropper.model.Model;

import junit.framework.TestCase;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class CameraTest extends TestCase {
    private static Matcher<Vector3> approx(final Vector3 expected, final float threshold) {
        return new TypeSafeMatcher<Vector3>() {
            @Override
            protected boolean matchesSafely(Vector3 actual) {
                return new Vector3(actual).sub(expected).len() < threshold;
            }
            @Override
            public void describeTo(Description description) {
                description.appendText("closer than " + threshold).appendText(" to ").appendValue(expected);
            }
        };
    }
    private static Matcher<Rectangle> approx(final Rectangle expected, final float threshold) {
        return new TypeSafeMatcher<Rectangle>() {
            private boolean isApprox(float a, float b) {
                return Math.abs(a - b) < threshold;
            }
            @Override
            protected boolean matchesSafely(Rectangle actual) {
                return isApprox(expected.x, actual.x) && isApprox(expected.y, actual.y)
                        && isApprox(expected.width, actual.width) && isApprox(expected.height, actual.height);
            }
            @Override
            public void describeTo(Description description) {
                description.appendValue(expected);
            }
        };
    }


    public static final float THRESHOLD = 0.01f;

    private static void assertTransforms(Matrix4 matrix, Vector2... mappings) {
        for (int i = 0; i < mappings.length; i += 2) {
            Vector2 from = mappings[i];
            Vector2 expected2 = mappings[i+1];
            Vector3 expected = new Vector3(expected2.x, expected2.y, 0);

            assertThat(new Vector3(from.x, from.y, 0).mul(matrix), approx(expected, THRESHOLD));
        }
    }

    private static Vector2 v(float x, float y) {
        return new Vector2(x, y);
    }

    public void testFixed() {
        // world = 1000x100
        Camera camera = Camera.fixed(new Grid(100, 10));

        // scale = 1
        camera.update(1000, 500);
        assertTransforms(camera.transform(),
                v(0, 0),     v(0, 0),
                v(123, 456), v(123, 456)
        );
        assertThat(camera.worldBounds(), approx(new Rectangle(0, 0, 1000, 500), THRESHOLD));

        // scale = 0.5
        camera.update(500, 500);
        assertTransforms(camera.transform(),
                v(0, 0),     v(0, 0),
                v(120, 400), v(60, 200)
        );
        assertThat(camera.worldBounds(), approx(new Rectangle(0, 0, 1000, 1000), THRESHOLD));
    }

    public void testLookingAt() {
        Model.HasPosition model = mock(Model.HasPosition.class);
        Camera camera = Camera.lookingAt(model, -100, 1000, 0.8f);

        // scale = 2 (from min world width), world base = (0, 0)
        when(model.position()).thenReturn(v(0, 0));
        camera.update(2000, 1000);
        assertTransforms(camera.transform(),
                v(0,    0),    v(1000, 200),
                v(-500, -100), v(0,    0),
                v(500,  400),  v(2000, 1000)
        );
        assertThat(camera.worldBounds(), approx(new Rectangle(-500, -100, 1000, 500), THRESHOLD));

        // scale = 0.25 (from max height fraction), world base = (3000, 0)
        when(model.position()).thenReturn(v(3000, 1500));
        camera.update(1000, 500);
        assertTransforms(camera.transform(),
                v(3000, 0),    v(500, 25),
                v(3000, 1500), v(500, 400),
                v(1000, 1900), v(0,   500)
        );
        assertThat(camera.worldBounds(), approx(new Rectangle(1000, -100, 4000, 2000), THRESHOLD));
    }
}
