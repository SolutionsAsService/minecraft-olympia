package dev.shadw.olympia;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Ambrosia: food that can be eaten at any hunger, and mends over time. */
public class AmbrosiaItem extends LoreItem {
	public AmbrosiaItem(Item.Properties properties, String loreKey) {
		super(properties, loreKey);
	}

	@Override
	public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
		ItemStack result = super.finishUsingItem(stack, level, entity);
		if (!level.isClientSide) {
			entity.addEffect(new MobEffectInstance(MobEffects.REGENERATION, ContentData.i("ambrosia", "regen_seconds") * 20,
					ContentData.i("ambrosia", "regen_amplifier")));
		}
		return result;
	}
}
