package dev.shadw.olympia;

import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricEntityType;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.levelgen.Heightmap;

/** The creatures: hoplite, cyclops and the Minotaur, each with a spawn egg. Hoplites and cyclopes also spawn in the wild. */
public final class OlympiaEntities {
	public static final EntityType<Hoplite> HOPLITE = register("hoplite", FabricEntityType.Builder.createMob(Hoplite::new, MobCategory.MONSTER,
			b -> b.spawnRestriction(SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Monster::checkMonsterSpawnRules)
					.defaultAttributes(Hoplite::createAttributes)).sized(0.6F, 1.95F).clientTrackingRange(8));

	public static final EntityType<Cyclops> CYCLOPS = register("cyclops", FabricEntityType.Builder.createMob(Cyclops::new, MobCategory.MONSTER,
			b -> b.spawnRestriction(SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Monster::checkMonsterSpawnRules)
					.defaultAttributes(Cyclops::createAttributes)).sized(0.6F, 1.95F).clientTrackingRange(10));

	public static final EntityType<Minotaur> MINOTAUR = register("minotaur", FabricEntityType.Builder.createMob(Minotaur::new, MobCategory.MONSTER,
			b -> b.spawnRestriction(SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Monster::checkMonsterSpawnRules)
					.defaultAttributes(Minotaur::createAttributes)).sized(0.6F, 1.95F).clientTrackingRange(12));

	public static final Item HOPLITE_SPAWN_EGG = egg("hoplite_spawn_egg", HOPLITE);
	public static final Item CYCLOPS_SPAWN_EGG = egg("cyclops_spawn_egg", CYCLOPS);
	public static final Item MINOTAUR_SPAWN_EGG = egg("minotaur_spawn_egg", MINOTAUR);

	private OlympiaEntities() {}

	private static <T extends net.minecraft.world.entity.Entity> EntityType<T> register(String path, EntityType.Builder<T> builder) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath(Mod.MOD_ID, path));
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	private static Item egg(String path, EntityType<? extends net.minecraft.world.entity.Mob> type) {
		ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath(Mod.MOD_ID, path));
		return Registry.register(BuiltInRegistries.ITEM, key, new SpawnEggItem(type, new Item.Properties().setId(key)));
	}

	/** Registers the entity types and their natural spawns (the Minotaur has none: it lives in the labyrinth). */
	public static void init() {
		BiomeModifications.addSpawn(BiomeSelectors.includeByKey(Biomes.PLAINS, Biomes.MEADOW, Biomes.SUNFLOWER_PLAINS), MobCategory.MONSTER, HOPLITE,
				ContentData.i("creatures.hoplite", "spawn_weight"), 1, 3);
		BiomeModifications.addSpawn(BiomeSelectors.includeByKey(Biomes.WINDSWEPT_HILLS, Biomes.STONY_PEAKS, Biomes.SAVANNA_PLATEAU), MobCategory.MONSTER,
				CYCLOPS, ContentData.i("creatures.cyclops", "spawn_weight"), 1, 1);
	}
}
