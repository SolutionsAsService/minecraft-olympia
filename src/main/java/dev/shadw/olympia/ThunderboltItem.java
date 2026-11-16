package dev.shadw.olympia;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** The Thunderbolt of Zeus: lightning where you look, for those Zeus has named Favored. It wears out and needs time between throws. */
public class ThunderboltItem extends LoreItem {
	public ThunderboltItem(Item.Properties properties, String loreKey) {
		super(properties, loreKey);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		if (!(level instanceof ServerLevel server) || !(player instanceof ServerPlayer sp)) {
			return InteractionResult.SUCCESS;
		}
		int needed = ContentData.i("thunderbolt", "required_stage");
		String god = ContentData.root().getAsJsonObject("thunderbolt").get("god").getAsString();
		if (Favor.stage(Favor.get(sp, god)) < needed) {
			sp.displayClientMessage(Component.literal("Zeus does not know you well enough. Offer at his altar until he names you "
					+ Favor.stageName(needed) + "."), true);
			return InteractionResult.FAIL;
		}
		double range = ContentData.d("thunderbolt", "range");
		Vec3 eye = player.getEyePosition();
		Vec3 end = eye.add(player.getLookAngle().scale(range));
		HitResult hit = level.clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
		Vec3 at = hit.getLocation();
		LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(server, EntitySpawnReason.TRIGGERED);
		if (bolt == null) {
			return InteractionResult.FAIL;
		}
		bolt.moveTo(at.x, at.y, at.z);
		bolt.setCause(sp);
		server.addFreshEntity(bolt);
		float damage = (float) ContentData.d("thunderbolt", "damage");
		for (LivingEntity target : server.getEntitiesOfClass(LivingEntity.class, new AABB(BlockPos.containing(at)).inflate(2.5), e -> e != player)) {
			target.hurtServer(server, server.damageSources().lightningBolt(), damage);
		}
		ItemStack stack = player.getItemInHand(hand);
		stack.hurtAndBreak(1, player, hand == InteractionHand.MAIN_HAND ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND);
		player.getCooldowns().addCooldown(stack, ContentData.i("thunderbolt", "cooldown_ticks"));
		return InteractionResult.SUCCESS;
	}
}
