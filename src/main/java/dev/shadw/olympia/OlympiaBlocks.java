package dev.shadw.olympia;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.PushReaction;

/** Marble and its family, three column orders, olive wood, the brazier, laurel and the gods' altars. */
public final class OlympiaBlocks {
	public static final String[] STONES = {"white_marble", "polished_marble", "weathered_marble", "cracked_marble", "black_marble",
			"pink_marble", "veined_marble", "golden_marble", "marble_bricks", "marble_tiles", "greek_mosaic", "roof_tile"};
	/** Stones that also come as stairs and slabs. */
	public static final String[] FAMILIES = {"white_marble", "polished_marble", "marble_bricks", "roof_tile"};
	public static final String[] COLUMNS = {"doric_column", "ionic_column", "corinthian_column"};
	public static final String[] GODS = {"zeus", "athena", "poseidon", "hermes", "apollo", "artemis", "ares", "demeter", "hera", "aphrodite", "hephaestus", "dionysus"};

	private static int count;
	public static final List<Block> BUILDING = new ArrayList<>();
	public static final Block[] ALTARS = new Block[GODS.length];

	static {
		for (String name : STONES) {
			Block block = register(name, key -> new Block(BlockBehaviour.Properties.of().strength(1.5F, 6.0F).sound(SoundType.STONE)
					.requiresCorrectToolForDrops().setId(key)));
			BUILDING.add(block);
			if (java.util.Arrays.asList(FAMILIES).contains(name)) {
				BUILDING.add(register(name + "_stairs", key -> new StairBlock(block.defaultBlockState(),
						BlockBehaviour.Properties.ofFullCopy(block).setId(key))));
				BUILDING.add(register(name + "_slab", key -> new SlabBlock(BlockBehaviour.Properties.ofFullCopy(block).setId(key))));
			}
		}
		for (String name : COLUMNS) {
			BUILDING.add(register(name, key -> new RotatedPillarBlock(BlockBehaviour.Properties.of().strength(2.0F, 6.0F)
					.sound(SoundType.STONE).requiresCorrectToolForDrops().setId(key))));
		}
	}

	public static final Block AMPHORA = register("amphora", key -> new Block(BlockBehaviour.Properties.of().strength(0.8F, 2.0F)
			.sound(SoundType.DECORATED_POT).setId(key)));

	public static final Block GREEK_BRAZIER = register("greek_brazier", key -> new BrazierBlock(
			BlockBehaviour.Properties.of().strength(2.0F, 6.0F).sound(SoundType.METAL).requiresCorrectToolForDrops()
					.lightLevel(state -> 14).setId(key)));

	public static final Block LAUREL = register("laurel", key -> new GroundPlantBlock(MobEffects.REGENERATION, 4.0F,
			BlockBehaviour.Properties.of().noCollission().instabreak().sound(SoundType.GRASS).pushReaction(PushReaction.DESTROY).setId(key)));

	public static final Block OLIVE_LOG = register("olive_log", key -> new RotatedPillarBlock(BlockBehaviour.Properties.of()
			.strength(2.0F).sound(SoundType.WOOD).setId(key)));

	public static final Block OLIVE_LEAVES = register("olive_leaves", key -> new LeavesBlock(BlockBehaviour.Properties.of()
			.strength(0.2F).randomTicks().sound(SoundType.GRASS).noOcclusion().isValidSpawn(Blocks::never).isSuffocating((s, g, p) -> false)
			.isViewBlocking((s, g, p) -> false).pushReaction(PushReaction.DESTROY).setId(key)));

	static {
		for (int i = 0; i < GODS.length; i++) {
			String god = GODS[i];
			ALTARS[i] = register(god + "_altar", key -> new AltarBlock(
					BlockBehaviour.Properties.of().strength(3.0F, 8.0F).sound(SoundType.STONE).requiresCorrectToolForDrops()
							.lightLevel(state -> 7).setId(key), god));
		}
	}

	private OlympiaBlocks() {}

	private static Block register(String path, Function<ResourceKey<Block>, Block> factory) {
		ResourceKey<Block> key = ResourceKey.create(Registries.BLOCK, ResourceLocation.fromNamespaceAndPath(Mod.MOD_ID, path));
		Block block = Registry.register(BuiltInRegistries.BLOCK, key, factory.apply(key));
		count++;
		ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, key.location());
		Registry.register(BuiltInRegistries.ITEM, itemKey, new BlockItem(block, new Item.Properties().setId(itemKey).useBlockDescriptionPrefix()));
		return block;
	}

	/** How many blocks this mod registers. */
	public static int count() {
		return count;
	}

	/** Touching this class registers the blocks. */
	public static void init() {}
}
