package com.dorr.chopperdropper.model;

import com.badlogic.gdx.math.Circle;
import com.badlogic.gdx.math.Vector2;
import com.dorr.chopperdropper.Index2;

import java.util.Set;

/** Basic interface for Models. */
public interface Model {
    interface HasPosition extends Model {
        Vector2 position();
    }

    interface Updatable extends Model {
        void update(float dt, Environment env);
    }

    interface Collidable extends Model {
        void onCollision(Model model, Environment env);
    }
    interface StaticCollidable extends Collidable {
        boolean isCollision(Set<Index2> indices);
    }
    interface DynamicCollidable extends Collidable {
        Circle bounds();
    }

    /** Provides a way for models to interact with their environment,
     * i.e. add new models, remove themselves, etc. */
    interface Environment {
        void add(Model model);
        void remove(Model model);
    }
}
