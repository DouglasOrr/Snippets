package com.dorr.chopperdropper.model;

import com.google.common.collect.Lists;

import junit.framework.TestCase;

import org.mockito.Mockito;

import static org.mockito.Matchers.any;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;

public class UpdaterTest extends TestCase {
    public void testUpdates() {
        Model.Updatable model = mock(Model.Updatable.class);
        World world = new World(Lists.newArrayList(model, mock(Model.class)), new Grid(10, 10));

        Updater updater = new Updater(world);
        updater.update(0.028f); // total: 0.028
        Mockito.verify(model, times(2)).update(eq(Updater.PHYSICS_DT), any(Model.Environment.class));

        updater.update(0.004f); // total: 0.032
        Mockito.verify(model, times(3)).update(eq(Updater.PHYSICS_DT), any(Model.Environment.class));

        updater.update(0.004f); // total: 0.036
        Mockito.verify(model, times(3)).update(eq(Updater.PHYSICS_DT), any(Model.Environment.class));
    }
}
