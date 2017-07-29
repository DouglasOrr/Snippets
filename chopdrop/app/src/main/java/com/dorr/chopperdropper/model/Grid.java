package com.dorr.chopperdropper.model;

import com.badlogic.gdx.math.Circle;
import com.badlogic.gdx.math.Rectangle;
import com.badlogic.gdx.math.Vector2;
import com.dorr.chopperdropper.Index2;

import java.util.HashSet;
import java.util.Set;

/** Transforms to and from 'grid world' coordinates */
public class Grid {
    public static final float BLOCK_SIZE = 10;
    public final int gridWidth;
    public final int gridHeight;

    public Grid(int width, int height) {
        gridWidth = width;
        gridHeight = height;
    }
    public Grid(Level level) {
        this(level.width(), level.height());
    }

    public float worldWidth() {
        return gridWidth * BLOCK_SIZE;
    }

    public float worldHeight() {
        return gridHeight * BLOCK_SIZE;
    }

    public Rectangle bounds(Index2 index) {
        return new Rectangle(index.x * BLOCK_SIZE, index.y * BLOCK_SIZE,
                             BLOCK_SIZE, BLOCK_SIZE);
    }

    public Vector2 center(Index2 index) {
        return new Vector2((index.x + 0.5f) * BLOCK_SIZE, (index.y + 0.5f) * BLOCK_SIZE);
    }

    public Set<Index2> intersections(Circle circle) {
        Set<Index2> results = new HashSet<Index2>();

        float r = circle.radius / BLOCK_SIZE;
        float cx = circle.x / BLOCK_SIZE;
        float cy = circle.y / BLOCK_SIZE;
        float r2 = r * r;

        // scan horizontal grid lines for crossovers
        int ymin = (int) Math.ceil(cy - r);
        int ymax = (int) Math.floor(cy + r);
        for (int y = ymin; y <= ymax; ++y) {
            float halfChord = (float) Math.sqrt(r2 - (y - cy) * (y - cy));
            int xbegin = (int) Math.floor(cx - halfChord);
            int xend = (int) Math.floor(cx + halfChord);
            for (int x = xbegin; x <= xend; ++x) {
                results.add(new Index2(x, y - 1));
                results.add(new Index2(x, y));
            }
        }

        // an additional scan line through the center of the circle
        // (for the cases where the circumference of the circle intersects a vertical
        // edge 0 or 2 times without crossing a horizontal edge)
        {
            int y = (int) Math.floor(cy);
            int xbegin = (int) Math.floor(cx - r);
            int xend = (int) Math.floor(cx + r);
            for (int x = xbegin; x <= xend; ++x) {
                results.add(new Index2(x, y));
            }
        }

        return results;
    }
}
