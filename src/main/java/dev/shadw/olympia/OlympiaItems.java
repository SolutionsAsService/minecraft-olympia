package dev.shadw.olympia;

import java.util.function.Function;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;

/** The relics (Thunderbolt, Thread of Ariadne), ambrosia and the drops. Potion ingredients come from potions.json. */
public final class OlympiaItems {
	public static final Item THUNDERBOLT = item("thunderbolt", p -> new ThunderboltItem(
			p.durability(ContentData.i("thunderbolt", "durability")).rarity(Rarity.EPIC).fireResistant(), "item.olympia.thunderbolt.lore"));

	public static final Item THREAD_OF_ARIADNE = item("thread_of_ariadne", p -> new ThreadItem(
			p.stacksTo(1).rarity(Rarity.RARE), "item.olympia.thread_of_ariadne.lore"));

	public static final Item AMBROSIA = item("ambrosia", p -> new AmbrosiaItem(
			p.rarity(Rarity.RARE).food(new FoodProperties.Builder().nutrition(ContentData.i("ambrosia", "nutrition")).saturationModifier(1.2F)
					.alwaysEdible().build()), "item.olympia.ambrosia.lore"));

	public static final Item OBOL = item("obol", p -> new LoreItem(p, "item.olympia.obol.lore"));
	public static final Item CYCLOPS_BLOODSTONE = item("cyclops_bloodstone", p -> new LoreItem(p.rarity(Rarity.UNCOMMON), "item.olympia.cyclops_bloodstone.lore"));
	public static final Item MINOTAUR_HORN = item("minotaur_horn", p -> new LoreItem(p.rarity(Rarity.RARE), "item.olympia.minotaur_horn.lore"));

	private OlympiaItems() {}

	private static Item item(String path, Function<Item.Properties, Item> factory) {
		ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath(Mod.MOD_ID, path));
		return Registry.register(BuiltInRegistries.ITEM, key, factory.apply(new Item.Properties().setId(key)));
	}

	/** Touching this class registers the items. */
	public static void init() {}
}
