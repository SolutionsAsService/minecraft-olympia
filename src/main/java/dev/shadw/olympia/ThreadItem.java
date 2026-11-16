package dev.shadw.olympia;

import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The Thread of Ariadne. Use it to tie the thread where you stand; use it anywhere afterwards and it shows the way back
 * (distance, compass direction, height, and a line of light along the first stretch). Sneak and use it to tie it somewhere new.
 */
public class ThreadItem extends LoreItem {
	private static final String[] DIRS = {"south", "south-west", "west", "north-west", "north", "north-east", "east", "south-east"};

	public ThreadItem(Item.Properties properties, String loreKey) {
		super(properties, loreKey);
	}

	/** "The thread leads north-west, 37 blocks, 4 up." for a vector from the player to the knot. */
	public static String describe(Vec3 delta) {
		double flat = Math.hypot(delta.x, delta.z);
		// 0 = south (+z), going clockwise to west (-x) as Minecraft's yaw does
		double yaw = Math.toDegrees(Math.atan2(-delta.x, delta.z));
		int index = Math.floorMod((int) Math.round(yaw / 45.0), 8);
		int up = (int) Math.round(delta.y);
		String height = Math.abs(up) < 2 ? "" : (up > 0 ? ", " + up + " up" : ", " + (-up) + " down");
		return "The thread leads " + DIRS[index] + ", " + (int) Math.round(flat) + " blocks" + height + ".";
	}

	/** The knot the held thread is tied to, or null if it is untied or tied in another dimension. */
	public static Vec3 knot(ItemStack stack, Level level) {
		CompoundTag tag = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
		if (!tag.contains("tx") || !level.dimension().location().toString().equals(tag.getString("dim"))) {
			return null;
		}
		return new Vec3(tag.getInt("tx") + 0.5, tag.getInt("ty") + 0.5, tag.getInt("tz") + 0.5);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		if (level.isClientSide) {
			return InteractionResult.SUCCESS;
		}
		CompoundTag tag = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
		String dim = level.dimension().location().toString();
		boolean tied = tag.contains("tx") && dim.equals(tag.getString("dim"));
		if (!tied || player.isShiftKeyDown()) {
			CompoundTag next = new CompoundTag();
			next.putInt("tx", player.getBlockX());
			next.putInt("ty", player.getBlockY());
			next.putInt("tz", player.getBlockZ());
			next.putString("dim", dim);
			stack.set(DataComponents.CUSTOM_DATA, CustomData.of(next));
			player.displayClientMessage(Component.literal("You tie the thread here."), true);
			return InteractionResult.SUCCESS;
		}
		Vec3 to = new Vec3(tag.getInt("tx") + 0.5, tag.getInt("ty") + 0.5, tag.getInt("tz") + 0.5);
		Vec3 delta = to.subtract(player.position());
		player.displayClientMessage(Component.literal(describe(delta)), true);
		if (level instanceof ServerLevel server && delta.length() > 0.5) {
			Vec3 dir = delta.normalize();
			for (int i = 1; i <= 14; i++) {
				Vec3 p = player.position().add(0, 0.6, 0).add(dir.scale(i * 0.8));
				server.sendParticles(ParticleTypes.END_ROD, p.x, p.y, p.z, 1, 0, 0, 0, 0);
			}
		}
		return InteractionResult.SUCCESS;
	}
}
