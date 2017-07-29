package com.dorr.chopperdropper;

import com.google.common.base.Objects;

/** An immutable 2D index pair (e.g. for indexing into a <code>Grid</code>). */
public class Index2 {
    public static Index2 idx(int x, int y) {
        return new Index2(x, y);
    }

    public final int x, y;

    public Index2(int x, int y) {
        this.x = x;
        this.y = y;
    }

    @Override
    public String toString() {
        return "(" + x + ", " + y + ")";
    }

    @Override
    public boolean equals(Object o) {
        if (this.getClass() != o.getClass()) {
            return false;
        }
        Index2 that = (Index2) o;
        return this.x == that.x
            && this.y == that.y;
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(x, y);
    }
}
