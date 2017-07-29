package com.dorr.chopperdropper.model;

import com.dorr.chopperdropper.Index2;
import com.google.common.base.Objects;
import com.google.common.collect.ImmutableBiMap;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static com.google.common.base.Preconditions.checkArgument;

/** 'Pure data' POJO for storing a level's terrain map.
 * <p>The terrain map can be specified in a file in our own format
 * (see demo.lvl), specifying the terrain shape, starting position,
 * defensive turret(s), and bombing objective(s).</p> */
public class Level {
    public enum Block {
        EMPTY, START, TERRAIN, OBJECTIVE, TURRET;

        private static final ImmutableBiMap<Block, Character> REPRESENTATIONS
                = ImmutableBiMap.of(
                    EMPTY,     ' ',
                    START,     's',
                    TERRAIN,   '*',
                    OBJECTIVE, 'o',
                    TURRET,    't'
                );
        public static Block fromChar(char c) {
            return REPRESENTATIONS.inverse().get(c);
        }
        public Character toChar() {
            return REPRESENTATIONS.get(this);
        }
    }
    public static final char COMMENT = '#';

    private final int mWidth;
    private final Block[] mBlocks;

    private Level(int width, Block[] blocks) {
        checkArgument(width == 0 || blocks.length % width == 0,
                "Number of blocks (%s) should be a multiple of the world width (%s)", blocks.length, width);
        mWidth = width;
        mBlocks = blocks;
    }

    public int width() { return mWidth; }

    public int height() { return mBlocks.length / mWidth; }

    public Block get(int x, int y) {
        checkArgument(0 <= x && x < mWidth && 0 <= y && y < height(),
                "Block index (%s, %s) out of bounds (%s, %s)", x, y, mWidth, height());
        return mBlocks[y * mWidth + x];
    }

    public Index2 find(Block block) {
        for (int idx = 0; idx < mBlocks.length; ++idx) {
            if (mBlocks[idx] == block) {
                return new Index2(idx % mWidth, idx / mWidth);
            }
        }
        return null;
    }

    public List<Index2> findAll(Block block) {
        List<Index2> indices = new ArrayList<Index2>();
        for (int idx = 0; idx < mBlocks.length; ++idx) {
            if (mBlocks[idx] == block) {
                indices.add(new Index2(idx % mWidth, idx / mWidth));
            }
        }
        return indices;
    }

    public static Level create(int width, Block... blocks) {
        return new Level(width, blocks);
    }

    private static String trimEnd(String s) {
        return s.replaceAll("\\s+$", "");
    }

    public static Level parse(BufferedReader in) throws IOException {
        List<String> lines = new ArrayList<String>();

        // read lines from input, remove comments & trailing whitespace
        {
            String line;
            while ((line = in.readLine()) != null) {
                int commentIdx = line.indexOf(COMMENT);
                if (commentIdx != -1) {
                    line = line.substring(0, commentIdx);
                }
                lines.add(trimEnd(line));
            }
        }

        // remove leading & trailing empty lines
        while (!lines.isEmpty() && lines.get(0).isEmpty()) {
            lines.remove(0);
        }
        while (!lines.isEmpty() && lines.get(lines.size() - 1).isEmpty()) {
            lines.remove(lines.size() - 1);
        }

        // the first lines are at the top of the terrain
        Collections.reverse(lines);

        // the world width is set to that of the longest line
        int height = lines.size();
        int width = 0;
        for (String line : lines) {
            width = Math.max(width, line.length());
        }

        // convert the list of lines to an array of blocks
        Block[] blocks = new Block[width * height];
        for (int y = 0; y < height; ++y) {
            String line = lines.get(y);
            for (int x = 0; x < width; ++x) {
                blocks[width * y + x] = (x < line.length())
                        ? Block.fromChar(line.charAt(x))
                        : Block.EMPTY;
            }
        }

        return new Level(width, blocks);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        final int height = height(), width = width();
        for (int y = height - 1; 0 <= y; --y) {
            sb.append('|');
            for (int x = 0; x < width; ++x) {
                sb.append(get(x, y).toChar());
            }
            sb.append('|');
            if (y != 0) {
                sb.append('\n');
            }
        }
        return sb.toString();
    }

    @Override
    public boolean equals(Object o) {
        if (getClass() != o.getClass()) {
            return false;
        }
        Level that = (Level) o;
        return this.mWidth == that.mWidth &&
               Arrays.equals(this.mBlocks, that.mBlocks);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(mWidth, Arrays.hashCode(mBlocks));
    }
}
