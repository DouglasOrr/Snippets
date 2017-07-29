package com.dorr.chopperdropper.model;

import android.util.Log;

import com.dorr.chopperdropper.Index2;
import com.google.common.base.Joiner;

import junit.framework.TestCase;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;

import static com.dorr.chopperdropper.model.Level.Block.EMPTY;
import static com.dorr.chopperdropper.model.Level.Block.OBJECTIVE;
import static com.dorr.chopperdropper.model.Level.Block.START;
import static com.dorr.chopperdropper.model.Level.Block.TERRAIN;
import static com.dorr.chopperdropper.model.Level.Block.TURRET;
import static com.dorr.chopperdropper.model.Level.create;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.nullValue;

public class LevelTest extends TestCase {
    private static Level parse(String... lines) throws IOException {
        return Level.parse(new BufferedReader(new StringReader(Joiner.on("\n").join(lines))));
    }

    public void testEquals() throws IOException {
        Level t2 = create(2,
                EMPTY, TERRAIN,
                TURRET, TERRAIN);

        assertThat(t2, equalTo(t2));
        assertThat(t2, equalTo(create(2,
                EMPTY, TERRAIN,
                TURRET, TERRAIN)));

        assertThat("different blocks", t2, not(create(2,
                OBJECTIVE, TERRAIN,
                TURRET, TERRAIN)));

        assertThat("different width", t2, not(create(4,
                EMPTY, TERRAIN,
                TURRET, TERRAIN)));
    }

    public void testOutOfBounds() throws IOException {
        try {
            create(2, EMPTY, EMPTY, EMPTY, EMPTY).get(2, 0);
            fail("Expected an exception");

        } catch (IllegalArgumentException e) {
            Log.d("DOUG", e.getMessage());
        }
    }

    public void testEmpty() throws IOException {
        assertThat(parse(), equalTo(create(0)));
        assertThat(parse("# this is a comment",
                         "\t",
                         "   ### and we have empty (when trimmed) lines ###",
                         "   "),
                   equalTo(create(0)));
    }

    public void testSingle() throws IOException {
        assertThat(parse("*"), equalTo(create(1, TERRAIN)));
        assertThat(parse("t"), equalTo(create(1, TURRET)));
        assertThat(parse("o"), equalTo(create(1, OBJECTIVE)));
        assertThat(parse("s"), equalTo(create(1, START)));

        assertThat(parse("*   #** trailing comment *tob # *tob **#"),
                   equalTo(create(1, TERRAIN)));
    }

    public void testMultiline() throws IOException {
        assertThat(
                parse("# rather nasty parsing example!",
                      "                               ",
                      "### begin ###",
                      " * o",
                      "",
                      "s*t ",
                      "    # should be ignored",
                      ""
                ),
                equalTo(create(4,
                        START, TERRAIN, TURRET, EMPTY,    // y=0
                        EMPTY, EMPTY,   EMPTY,  EMPTY,    // y=1
                        EMPTY, TERRAIN, EMPTY,  OBJECTIVE // y=2
                ))
        );
    }

    public void testFind() {
        Level level = create(3,
                TERRAIN, START, TERRAIN,
                EMPTY, EMPTY, OBJECTIVE);
        assertThat(level.find(START), equalTo(new Index2(1, 0)));
        assertThat(level.find(OBJECTIVE), equalTo(new Index2(2, 1)));
        assertThat(level.find(TURRET), nullValue());
    }
}
