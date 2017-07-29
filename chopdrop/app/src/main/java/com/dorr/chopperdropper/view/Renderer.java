package com.dorr.chopperdropper.view;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.Pixmap;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.BitmapFont;
import com.badlogic.gdx.graphics.g2d.Sprite;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.math.Matrix4;
import com.badlogic.gdx.math.Rectangle;
import com.badlogic.gdx.math.Vector2;
import com.dorr.chopperdropper.Index2;
import com.dorr.chopperdropper.model.AmmoPoint;
import com.dorr.chopperdropper.model.Bomb;
import com.dorr.chopperdropper.model.Bullet;
import com.dorr.chopperdropper.model.Grid;
import com.dorr.chopperdropper.model.Heli;
import com.dorr.chopperdropper.model.Model;
import com.dorr.chopperdropper.model.Target;
import com.dorr.chopperdropper.model.Terrain;
import com.dorr.chopperdropper.model.Turret;
import com.dorr.chopperdropper.model.World;
import com.google.common.collect.ImmutableList;
import com.google.common.primitives.Ints;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/** This class has the auspicious task of organising the whole
 * rendering job. */
public class Renderer {
    private final World mWorld;
    private final Camera mCamera;
    private final SpriteBatch mBatch;
    private final BitmapFont mFont;
    private final Texture mHeliTexture;
    private final Texture mExplosionTexture;
    private final Texture mBombTexture;
    private final Texture mTargetTexture;
    private final Texture mTurretBaseTexture;
    private final Texture mTurretGunTexture;
    private final Texture mSolidTexture;

    private static final List<Color> TERRAIN_COLORS = ImmutableList.of(
            new Color(0x85FFB7FF),
            new Color(0x75E884FF),
            new Color(0xA4FF90FF),
            new Color(0xB2E877FF),
            new Color(0xEEFF7FFF)
    );
    private static final Color BG_COLOR = new Color(0x3DCBE8FF);
    private static final Color HELI_COLOR = new Color(0xB24816FF);
    private static final Color AMMO_COLOR = new Color(0xFFFFFF60);

    public static final float HELI_SIZE = 15;
    public static final float BOMB_SIZE = 6;
    public static final float BOMB_EXPLOSION_SIZE = 15;
    public static final int FLOOR_DEPTH = 2;
    public static final int BULLET_HALF_SIZE = 1;

    private static Texture solidTexture() {
        Pixmap pm = new Pixmap(1, 1, Pixmap.Format.RGBA8888);
        pm.setColor(Color.WHITE);
        pm.fill();
        return new Texture(pm);
    }

    public Renderer(World world) {
        mWorld = world;
        mCamera = Camera.lookingAt(mWorld.heli(), -FLOOR_DEPTH * Grid.BLOCK_SIZE, Grid.BLOCK_SIZE * 20, 0.8f);
        mBatch = new SpriteBatch();
        mFont = new BitmapFont();
        mFont.setColor(Color.WHITE);
        mHeliTexture = new Texture("heli.png");
        mExplosionTexture = new Texture("explosion.png");
        mBombTexture = new Texture("bomb.png");
        mTargetTexture = new Texture("target.png");
        mTurretBaseTexture = new Texture("turret_base.png");
        mTurretGunTexture = new Texture("turret_gun.png");
        mSolidTexture = solidTexture();
    }

    public void dispose() {
        mSolidTexture.dispose();
        mTargetTexture.dispose();
        mBombTexture.dispose();
        mExplosionTexture.dispose();
        mHeliTexture.dispose();
        mFont.dispose();
        mBatch.dispose();
    }

    private static abstract class Item {
        public static final Comparator<Item> COMPARE_PRIORITY = new Comparator<Item>() {
            @Override
            public int compare(Item left, Item right) {
                return Ints.compare(left.priority, right.priority);
            }
        };

        public final int priority;

        private Item(int priority) {
            this.priority = priority;
        }

        public abstract void draw(SpriteBatch batch);

        public static Item sprite(int priorty, final Sprite sprite) {
            return new Item(priorty) {
                @Override
                public void draw(SpriteBatch batch) {
                    sprite.draw(batch);
                }
            };
        }

        public static Item text(int priority, final BitmapFont font,
                                final String text, final float x, final float y) {
            return new Item(priority) {
                @Override
                public void draw(SpriteBatch batch) {
                    font.draw(batch, text, x, y);
                }
            };
        }
    }

    public void render() {
        mCamera.update(Gdx.graphics.getWidth(), Gdx.graphics.getHeight());

        List<Item> items = new ArrayList<Item>();

        // generate renderable items
        for (Model model : mWorld.models) {
            List<Item> i = Collections.emptyList();
            if (model instanceof Heli) {
                i = render((Heli) model);
            } else if (model instanceof Terrain) {
                i = render((Terrain) model);
            } else if (model instanceof Target) {
                i = render((Target) model);
            } else if (model instanceof AmmoPoint) {
                i = render ((AmmoPoint) model);
            } else if (model instanceof Bomb) {
                i = render((Bomb) model);
            } else if (model instanceof Turret) {
                i = render((Turret) model);
            } else if (model instanceof Bullet) {
                i = render((Bullet) model);
            }
            items.addAll(i);
        }

        // sort
        Collections.sort(items, Item.COMPARE_PRIORITY);

        // draw
        Gdx.gl.glClearColor(BG_COLOR.r, BG_COLOR.g, BG_COLOR.b, BG_COLOR.a);
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT);

        mBatch.begin();
        mBatch.setTransformMatrix(mCamera.transform());
        for (Item item : items) {
            item.draw(mBatch);
        }

        mBatch.setTransformMatrix(new Matrix4()); // switch back to identity
        frameRate().draw(mBatch);
        mBatch.end();
    }

    private Item frameRate() {
        return Item.text(100, mFont, Gdx.graphics.getFramesPerSecond() + " fps", 0, mFont.getLineHeight());
    }

    private List<Item> render(Heli heli) {
        Vector2 position = heli.position();

        List<Item> items = new ArrayList<Item>(2);
        Sprite main = new Sprite(mHeliTexture);
        main.setSize(HELI_SIZE, HELI_SIZE);
        main.setOriginCenter();
        main.setColor(HELI_COLOR);
        main.setPosition(position.x - main.getWidth() / 2, position.y - main.getHeight() / 2);
        main.setRotation(heli.angle() * MathUtils.radiansToDegrees);
        items.add(Item.sprite(0, main));

        if (heli.state() == Heli.State.CRASHED) {
            Sprite explosion = new Sprite(mExplosionTexture);
            explosion.setSize(HELI_SIZE, HELI_SIZE);
            explosion.setPosition(position.x - HELI_SIZE / 2, position.y - HELI_SIZE / 2);
            items.add(Item.sprite(1, explosion));
        }
        return items;
    }

    private static void setBounds(Sprite sprite, Rectangle bounds) {
        sprite.setBounds(bounds.x, bounds.y, bounds.width, bounds.height);
    }

    // component for generating colours for blocks, that
    // - are random
    // - once generated, are fixed (will never change)
    // - do not contain adjacent identical colours
    private Random mRandom = new Random();
    private Map<Index2, Color> mBlockColors = new HashMap<Index2, Color>();
    private Color nextRandomColor(Index2 idx) {
        List<Color> options = new ArrayList<Color>(TERRAIN_COLORS);
        options.remove(mBlockColors.get(new Index2(idx.x - 1, idx.y)));
        options.remove(mBlockColors.get(new Index2(idx.x + 1, idx.y)));
        options.remove(mBlockColors.get(new Index2(idx.x, idx.y - 1)));
        options.remove(mBlockColors.get(new Index2(idx.x, idx.y + 1)));
        return options.get(mRandom.nextInt(options.size()));
    }
    private Color getBlockColor(Index2 idx) {
        Color color = mBlockColors.get(idx);
        if (color == null) {
            color = nextRandomColor(idx);
            mBlockColors.put(idx, color);
        }
        return color;
    }

    private List<Item> render(Terrain terrain) {
        Rectangle bounds = mCamera.worldBounds();
        int minX = (int) Math.floor(bounds.x / Grid.BLOCK_SIZE);
        int maxX = (int) Math.ceil((bounds.x + bounds.width) / Grid.BLOCK_SIZE);

        List<Item> items = new ArrayList<Item>(terrain.get().size() + FLOOR_DEPTH * (maxX - minX));

        // draw the floor
        for (int y = -FLOOR_DEPTH; y < 0; ++y) {
            for (int x = minX; x < maxX; ++x) {
                Index2 idx = new Index2(x, y);
                Sprite sprite = new Sprite(mSolidTexture);
                sprite.setColor(getBlockColor(idx));
                setBounds(sprite, mWorld.grid.bounds(idx));
                items.add(Item.sprite(-10, sprite));
            }
        }

        // draw the rest of the terrain
        for (Index2 idx : terrain.get()) {
            Sprite sprite = new Sprite(mSolidTexture);
            sprite.setColor(getBlockColor(idx));
            setBounds(sprite, mWorld.grid.bounds(idx));
            items.add(Item.sprite(-10, sprite));
        }
        return items;
    }

    private List<Item> render(Target target) {
        List<Item> items = new ArrayList<Item>(2);
        Rectangle bounds = mWorld.grid.bounds(target.position());

        Sprite sprite = new Sprite(mTargetTexture);
        setBounds(sprite, bounds);
        items.add(Item.sprite(-10, sprite));

        if (target.state() == Target.State.DEAD) {
            Sprite explosion = new Sprite(mExplosionTexture);
            explosion.setSize(BOMB_EXPLOSION_SIZE, BOMB_EXPLOSION_SIZE);
            explosion.setPosition(
                    bounds.x + bounds.width / 2 - BOMB_EXPLOSION_SIZE / 2,
                    bounds.y + bounds.height / 2 - BOMB_EXPLOSION_SIZE / 2
            );
            items.add(Item.sprite(1, explosion));
        }
        return items;
    }

    private List<Item> render(AmmoPoint ammoPoint) {
        Sprite shade = new Sprite(mSolidTexture);
        setBounds(shade, mWorld.grid.bounds(ammoPoint.position()));
        shade.setColor(AMMO_COLOR);
        return Collections.singletonList(Item.sprite(-10, shade));
    }

    private List<Item> render(Bomb bomb) {
        Sprite sprite = new Sprite(mBombTexture);
        sprite.setSize(BOMB_SIZE, BOMB_SIZE);
        sprite.setOriginCenter();
        sprite.setColor(HELI_COLOR);
        Vector2 position = bomb.position();
        sprite.setPosition(position.x - sprite.getWidth() / 2, position.y - sprite.getHeight() / 2);
        return Collections.singletonList(Item.sprite(-1, sprite));
    }

    private List<Item> render(Turret turret) {
        Sprite base = new Sprite(mTurretBaseTexture);
        setBounds(base, mWorld.grid.bounds(turret.index()));

        Sprite gun = new Sprite(mTurretGunTexture);
        gun.setSize(Grid.BLOCK_SIZE, Grid.BLOCK_SIZE);
        gun.setOriginCenter();
        Vector2 position = mWorld.grid.center(turret.index());
        gun.setPosition(position.x - gun.getWidth() / 2, position.y - gun.getHeight() / 2);
        gun.setRotation(turret.angle() * MathUtils.radiansToDegrees);

        return ImmutableList.of(Item.sprite(-2, base), Item.sprite(-3, gun));
    }

    private List<Item> render(Bullet bullet) {
        Sprite sprite = new Sprite(mSolidTexture);
        sprite.setColor(Color.BLACK);
        Vector2 p = bullet.position();
        sprite.setBounds(
                p.x - BULLET_HALF_SIZE, p.y - BULLET_HALF_SIZE,
                BULLET_HALF_SIZE, BULLET_HALF_SIZE
        );
        return ImmutableList.of(Item.sprite(-4, sprite));
    }
}
