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
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.level.levelgen.Heightmap;

/** The hand-written creatures (mounts). Every walking monster is defined in mobs/*.json and generated into the mobs package. */
public final class OlympiaEntities {
	public static final EntityType<Pegasus> PEGASUS = register("pegasus", FabricEntityType.Builder.createMob(Pegasus::new, MobCategory.CREATURE,
			b -> b.spawnRestriction(SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING, Animal::checkAnimalSpawnRules)
					.defaultAttributes(Pegasus::createAttributes)).sized(1.4F, 1.7F).passengerAttachments(1.55F).clientTrackingRange(10));

	public static final Item PEGASUS_SPAWN_EGG = egg("pegasus_spawn_egg", PEGASUS);

	private OlympiaEntities() {}

	private static <T extends net.minecraft.world.entity.Entity> EntityType<T> register(String path, EntityType.Builder<T> builder) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath(Mod.MOD_ID, path));
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	private static Item egg(String path, EntityType<? extends Mob> type) {
		ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath(Mod.MOD_ID, path));
		return Registry.register(BuiltInRegistries.ITEM, key, new SpawnEggItem(type, new Item.Properties().setId(key)));
	}

	/** Registers the natural spawns: a rare herd on high meadows. */
	public static void init() {
		BiomeModifications.addSpawn(BiomeSelectors.includeByKey(ResourceKey.create(Registries.BIOME, ResourceLocation.parse("minecraft:meadow")),
				ResourceKey.create(Registries.BIOME, ResourceLocation.parse("minecraft:cherry_grove"))), MobCategory.CREATURE, PEGASUS, 2, 1, 2);
	}
}
