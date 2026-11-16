package dev.shadw.olympia;

import java.util.List;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** A brewing ingredient with a one-line lore tooltip. */
public class LoreItem extends Item {
	private final String loreKey;

	public LoreItem(Item.Properties properties, String loreKey) {
		super(properties);
		this.loreKey = loreKey;
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
		tooltip.add(Component.translatable(loreKey).withStyle(net.minecraft.ChatFormatting.GRAY, net.minecraft.ChatFormatting.ITALIC));
	}
}
