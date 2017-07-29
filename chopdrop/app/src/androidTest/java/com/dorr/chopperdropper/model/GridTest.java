package com.dorr.chopperdropper.model;

import com.badlogic.gdx.math.Circle;

import junit.framework.TestCase;

import static com.dorr.chopperdropper.Index2.idx;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;

public class GridTest extends TestCase {
    private static final float B = Grid.BLOCK_SIZE;

    public void testIntersections() {
        Grid grid = new Grid(10, 10);

        assertThat("simple: whole circle in one block",
                grid.intersections(new Circle(2.5f * B, 6.5f * B, 0.45f * B)),
                containsInAnyOrder(idx(2, 6)));

        assertThat("out of bounds is fine",
                grid.intersections(new Circle(-0.5f * B, 100.5f * B, 0.0f)),
                containsInAnyOrder(idx(-1, 100)));

        assertThat("overlapping a corner",
                grid.intersections(new Circle(1.1f * B, 1.9f * B, 0.45f * B)),
                containsInAnyOrder(idx(0, 1), idx(1, 1), idx(0, 2), idx(1, 2)));

        assertThat("horizontal edge",
                grid.intersections(new Circle(3.5f * B, 1.75f * B, 0.45f * B)),
                containsInAnyOrder(idx(3, 1), idx(3, 2)));

        assertThat("vertical edge",
                grid.intersections(new Circle(1.75f * B, 3.5f * B, 0.45f * B)),
                containsInAnyOrder(idx(1, 3), idx(2, 3)));

        assertThat("large circle",
                grid.intersections(new Circle(2.5f * B, B, 1.01f * B)),
                containsInAnyOrder(
                        idx(2, -1),
                        idx(1, 0), idx(2, 0), idx(3, 0),
                        idx(1, 1), idx(2, 1), idx(3, 1),
                        idx(2, 2)
                ));
    }
}
