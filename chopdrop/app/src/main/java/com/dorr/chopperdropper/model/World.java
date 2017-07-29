package com.dorr.chopperdropper.model;

import com.badlogic.gdx.Gdx;
import com.dorr.chopperdropper.Index2;
import com.dorr.chopperdropper.control.HeliTouchControl;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

public class World {
    public final List<Model> models;
    public final Grid grid;

    public World(List<Model> models, Grid grid) {
        this.models = models;
        this.grid = grid;
    }

    public static class Env implements Model.Environment {
        private final HashSet<Model> mToAdd = new HashSet<Model>();
        private final HashSet<Model> mToRemove = new HashSet<Model>();
        @Override
        public void add(Model model) { mToAdd.add(model); }
        @Override
        public void remove(Model model) { mToRemove.add(model); }
    }
    public Env beginUpdate() {
        return new Env();
    }
    public void endUpdate(Env env) {
        models.removeAll(env.mToRemove);
        models.addAll(env.mToAdd);
    }

    public Heli heli() {
        for (Model model : models) {
            if (model instanceof Heli) {
                return (Heli) model;
            }
        }
        return null;
    }

    public static World create(Level level) {
        HeliTouchControl control = new HeliTouchControl();
        Gdx.input.setInputProcessor(control); // TODO: side effects -> bad

        Grid grid = new Grid(level);

        List<Model> models = new ArrayList<Model>();

        models.add(Terrain.create(level));
        models.add(new Target(level.find(Level.Block.OBJECTIVE)));

        Index2 start = level.find(Level.Block.START);
        models.add(new AmmoPoint(start));
        Heli heli = new Heli(grid.center(start), control);
        models.add(heli);

        for (Index2 idx : level.findAll(Level.Block.TURRET)) {
            models.add(new Turret(idx, grid, heli));
        }

        return new World(models, grid);
    }
}
