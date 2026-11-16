package dev.shadw.olympia;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/** A god's offering altar. Use it with an offering in hand to raise your favor, and with an empty hand to see where you stand. */
public class AltarBlock extends Block {
	private final String god;

	public AltarBlock(Properties properties, String god) {
		super(properties);
		this.god = god;
	}

	@Override
	protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
			InteractionHand hand, BlockHitResult hit) {
		if (Favor.worth(god, stack) == 0) {
			return InteractionResult.TRY_WITH_EMPTY_HAND;
		}
		if (player instanceof ServerPlayer sp) {
			Favor.offer(sp, god, stack);
		}
		return InteractionResult.SUCCESS;
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
		if (player instanceof ServerPlayer sp) {
			JsonObject g = Favor.god(god);
			int favor = Favor.get(sp, god);
			StringBuilder wants = new StringBuilder();
			for (JsonElement e : g.getAsJsonArray("offerings")) {
				String id = e.getAsJsonObject().get("item").getAsString();
				wants.append(wants.length() == 0 ? "" : ", ").append(id.substring(id.indexOf(':') + 1).replace('_', ' '));
			}
			sp.displayClientMessage(Component.literal(g.get("name").getAsString() + ", " + g.get("title").getAsString() + ". Favor " + favor
					+ " (" + Favor.stageName(Favor.stage(favor)) + "). Offer: " + wants + "."), true);
		}
		return InteractionResult.SUCCESS;
	}

	@Override
	public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
		if (random.nextInt(8) == 0) {
			level.addParticle(ParticleTypes.ENCHANT, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5,
					random.nextGaussian() * 0.3, 0.4, random.nextGaussian() * 0.3);
		}
	}
}
