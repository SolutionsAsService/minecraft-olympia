package dev.shadw.olympia;

import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;

/** A citizen-soldier in bronze: shield and blade, burns in no sun, calls no reinforcements, and drops obols. */
public class Hoplite extends Zombie {
	public Hoplite(EntityType<? extends Hoplite> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Zombie.createAttributes()
				.add(Attributes.MAX_HEALTH, ContentData.d("creatures.hoplite", "health"))
				.add(Attributes.ATTACK_DAMAGE, ContentData.d("creatures.hoplite", "damage"))
				.add(Attributes.ARMOR, ContentData.d("creatures.hoplite", "armor"))
				.add(Attributes.MOVEMENT_SPEED, ContentData.d("creatures.hoplite", "speed"))
				.add(Attributes.SPAWN_REINFORCEMENTS_CHANCE, 0.0);
	}

	@Override
	protected void populateDefaultEquipmentSlots(RandomSource random, DifficultyInstance difficulty) {
		setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.IRON_SWORD));
		setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(Items.SHIELD));
		setDropChance(EquipmentSlot.MAINHAND, 0.05F);
		setDropChance(EquipmentSlot.OFFHAND, 0.05F);
	}

	@Override
	protected boolean isSunSensitive() {
		return false;
	}

	@Override
	protected boolean convertsInWater() {
		return false;
	}

	@Override
	public boolean isBaby() {
		return false;
	}
}
