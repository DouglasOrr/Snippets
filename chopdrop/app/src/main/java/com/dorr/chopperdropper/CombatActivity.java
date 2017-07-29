package com.dorr.chopperdropper;

import android.os.Bundle;

import com.badlogic.gdx.ApplicationAdapter;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.backends.android.AndroidApplication;
import com.badlogic.gdx.backends.android.AndroidApplicationConfiguration;
import com.dorr.chopperdropper.model.Level;
import com.dorr.chopperdropper.model.Updater;
import com.dorr.chopperdropper.model.World;
import com.dorr.chopperdropper.view.Renderer;
import com.google.common.base.Throwables;
import com.google.common.io.Closeables;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

/** The main gameplay activity. If you're here, you're playing */
public class CombatActivity extends AndroidApplication {
    private final ApplicationAdapter mGame = new ApplicationAdapter() {
        private World mWorld;
        private Updater mUpdater;
        private Renderer mRenderer;

        private Level loadLevel(String name) {
            BufferedReader reader = null;
            try {
                reader = new BufferedReader(new InputStreamReader(Gdx.files.internal(name).read()));
                return Level.parse(reader);

            } catch (IOException e) {
                throw Throwables.propagate(e);

            } finally {
                Closeables.closeQuietly(reader);
            }
        }

        @Override
        public void create() {
            super.create();
            mWorld = World.create(loadLevel("demo.lvl"));
            mUpdater = new Updater(mWorld);
            mRenderer = new Renderer(mWorld);
        }

        @Override
        public void dispose() {
            super.dispose();
            mRenderer.dispose();
        }

        @Override
        public void render() {
            super.render();
            mUpdater.update(Gdx.graphics.getRawDeltaTime());
            mRenderer.render();
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        initialize(mGame, new AndroidApplicationConfiguration());
    }
}
